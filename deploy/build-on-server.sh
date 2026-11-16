#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
[[ $# == 1 && $(id -u) == 0 ]]
release=$(realpath -e -- "$1")
[[ "$release" =~ ^/opt/homepage/releases/([0-9a-f]{40})$ ]]
revision=${BASH_REMATCH[1]}
source_dir="$release/source"
[[ -d "$source_dir" && ! -L "$source_dir" ]]
exec 9>/var/lock/site-build.lock
flock -w 3600 9
if [[ -d /opt/rdb/shared ]]; then
  exec 7>/opt/rdb/shared/build.lock
  flock -w 3600 7
fi
exec 8>/opt/homepage/shared/build.lock
flock -w 3600 8
python3 "$source_dir/deploy/source-snapshot.py" verify "$revision" "$source_dir" "$release/source-manifest.json"
manifest_hash=$(sha256sum "$release/source-manifest.json" | cut -d ' ' -f 1)
runtime=$(python3 -c 'import json; print(json.load(open("/opt/homepage/shared/runtime-image.json"))["image"])')
runtime_id=$(python3 -c 'import json; print(json.load(open("/opt/homepage/shared/runtime-image.json"))["image_id"])')
[[ "$runtime" =~ ^homepage-runtime-base:[a-zA-Z0-9._-]+$ && "$runtime_id" =~ ^sha256:[0-9a-f]{64}$ ]]
[[ "$(docker image inspect "$runtime" --format '{{.Id}}')" == "$runtime_id" ]]
python3 - "$source_dir/deploy/Dockerfile.server" <<'PY'
import hashlib,json,pathlib,sys
expected=json.load(open('/opt/homepage/shared/runtime-image.json'))['dockerfile_sha256']
assert hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest()==expected, 'Runtime recipe changed; review the pinned base and deployment recipe first.'
PY
receipt="$release/build-receipt.json"
if existing=$(docker image inspect "homepage:$revision" --format '{{.Id}}' 2>/dev/null); then
  python3 - "$receipt" "$existing" "$manifest_hash" "$runtime_id" "$release/site-manifest.json" <<'PY'
import hashlib,json,pathlib,sys
r=json.load(open(sys.argv[1]))
assert r=={'image_id':sys.argv[2],'manifest_sha256':sys.argv[3],'runtime_id':sys.argv[4],'tests_passed':True,'site_manifest_sha256':hashlib.sha256(pathlib.Path(sys.argv[5]).read_bytes()).hexdigest()}
PY
else
  [[ $(df -B1 --output=avail /opt/homepage | tail -1) -gt 5368709120 ]]
  [[ $(awk '/MemAvailable:/ {print $2}' /proc/meminfo) -gt 524288 ]]
  python3 -B "$source_dir/deploy/test-site-package.py"
  python3 -B "$source_dir/deploy/test-release.py"
  python3 "$source_dir/deploy/site-package.py" check "$source_dir"
  bundle=$(mktemp -d "$release/package.XXXXXX")
  rmdir "$bundle"
  cleanup() {
    if [[ "$bundle" == "$release"/package.* && -d "$bundle" ]]; then
      rm -rf -- "$bundle"
    fi
  }
  trap cleanup EXIT
  python3 "$source_dir/deploy/site-package.py" build "$source_dir" "$bundle"
  docker run --rm --network none --read-only \
    --entrypoint /usr/bin/caddy \
    --mount "type=bind,src=$bundle/Caddyfile,dst=/etc/caddy/Caddyfile,readonly" \
    "$runtime_id" validate --config /etc/caddy/Caddyfile --adapter caddyfile
  docker buildx build --load --pull=false --network=none \
    --resource memory=512m --resource memory-swap=512m \
    --resource cpu-quota=100000 --resource cpu-period=100000 \
    --build-arg "HOMEPAGE_RUNTIME_IMAGE=$runtime" \
    --label "org.opencontainers.image.revision=$revision" \
    --label org.opencontainers.image.source=https://github.com/OXOOOOX/llm-interactive-course \
    --file "$source_dir/deploy/Dockerfile.server" --tag "homepage-build:$revision" "$bundle" </dev/null
  [[ "$(docker image inspect "homepage-build:$revision" --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}')" == "$revision" ]]
  image_id=$(docker image inspect "homepage-build:$revision" --format '{{.Id}}')
  install -m 644 "$bundle/site-manifest.json" "$release/site-manifest.json"
  python3 - "$receipt" "$image_id" "$manifest_hash" "$runtime_id" "$release/site-manifest.json" <<'PY'
import hashlib,json,os,pathlib,sys
p=pathlib.Path(sys.argv[1]);tmp=p.with_suffix('.tmp')
tmp.write_text(json.dumps({'image_id':sys.argv[2],'manifest_sha256':sys.argv[3],'runtime_id':sys.argv[4],'tests_passed':True,'site_manifest_sha256':hashlib.sha256(pathlib.Path(sys.argv[5]).read_bytes()).hexdigest()})+'\n')
tmp.chmod(0o600);os.replace(tmp,p)
PY
  docker tag "homepage-build:$revision" "homepage:$revision"
fi
for file in compose.yaml deploy.sh release.py; do
  install -m 644 "$source_dir/deploy/$file" "$release/$file"
done
printf 'Verified server build ready: %s\n' "$revision"
