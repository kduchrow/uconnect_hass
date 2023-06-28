# Load platform example

This is an example of an integration loading its platforms from its own set up, and passing information on to the platforms.

Use this approach only if your integration is configured solely via `configuration.yaml` and does not use config entries.

### Installation

Copy this folder to `<config_dir>/custom_components/uconnect_hass/`.

Add the following entry in your `configuration.yaml`:

```yaml
uconnect_sensor:
  username: !secret uconnect_user
  password: !secret uconnect_pw
  pin: !secret uconnect_pin
```
