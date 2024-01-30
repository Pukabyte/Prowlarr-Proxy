Port = 8000

```version: "3"

services:
  proxy:
    restart: unless-stopped
    container_name: proxy
    image: pukabyte/proxy:latest
    hostname: proxy
    environment:
      - PUID=1000
      - PGID=1000
      - prowlarr_url=http://your_prowlarr_url
      - x_api_key=your_x_api_key
      - auth_token=your_auth_token
      - proxy_url=http://your_proxy_url
    ports:
      - "8000:8000"```