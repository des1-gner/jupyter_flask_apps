```markdown
# Running Flask Apps on Amazon SageMaker Studio

A quick guide to building and testing Flask web applications directly inside
Amazon SageMaker Studio using JupyterLab's built-in proxy support.

---

## Overview

SageMaker Studio runs a managed JupyterLab environment that includes a
built-in URL proxy. This means you can run a Flask web server inside your
notebook instance and access it through your browser, without needing to
open any ports or configure any networking.

There are two approaches covered in this guide:

1. **SageMaker Built-in Proxy** - Simple, zero-configuration, works immediately
2. **Jupyter Server Proxy** - More feature-rich, requires a one-time setup and
   restart

---

## Prerequisites

- An active Amazon SageMaker Studio domain
- A JupyterLab app running on SageMaker Studio
- Python 3.x (pre-installed in SageMaker environments)
- Flask (install via pip if not already present)

---

## Option 1: SageMaker Built-in Proxy (Recommended for Simple Use Cases)

SageMaker Studio automatically proxies traffic from a special URL path to any
port running on your instance. No additional packages or configuration needed.

### Step 1: Create your Flask app

Create a file called `app.py` in your JupyterLab file browser:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask on SageMaker!"

if __name__ == '__main__':
    # Must bind to 0.0.0.0 and a consistent port for the proxy to work
    app.run(host='0.0.0.0', port=8050, debug=True)
```

> **Important:** You must bind to `0.0.0.0` (all interfaces), not `127.0.0.1`
> or `localhost`. The proxy will not be able to reach your app otherwise.

### Step 2: Start the Flask server

In a notebook cell or terminal, run:

```bash
python app.py
```

Or from a notebook cell:

```python
import subprocess
import sys

subprocess.Popen(
    [sys.executable, 'app.py'],
    stdout=open('flask.log', 'w'),
    stderr=open('flask.log', 'w')
)
```

### Step 3: Access your app

Your Flask app will be available at:

```
https://<app-id>.studio.<region>.sagemaker.aws/jupyterlab/default/proxy/8050/
```

You can find your `<app-id>` and `<region>` from the SageMaker Studio URL in
your browser.

---

## Option 2: Jupyter Server Proxy

The `jupyter-server-proxy` package is an open-source JupyterLab extension that
provides more control over how background processes are proxied, including
named URL paths and process lifecycle management.

More information: https://jupyter-server-proxy.readthedocs.io/en/latest/

### Step 1: Install and configure

Run the following in a notebook cell:

```python
import os

# Install the package
import subprocess, sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q',
                       'jupyter-server-proxy'])

# Write the server proxy config
config_path = os.path.expanduser("~/.jupyter/jupyter_notebook_config.py")
os.makedirs(os.path.dirname(config_path), exist_ok=True)

with open(config_path, 'w') as f:
    f.write("""
c.ServerProxy.servers = {
    'flask': {
        'command': ['python', 'app.py'],
        'port': 8050,
        'timeout': 60
    }
}
""")
```

### Step 2: Enable the extension

```bash
jupyter server extension enable --py jupyter_server_proxy
```

### Step 3: Restart your JupyterLab app

This is a one-time requirement. Go back to the SageMaker Studio UI, stop your
JupyterLab app, and start it again. The extension will be active from this
point forward and does not need to be re-enabled on subsequent launches
(as long as your home directory persists).

### Step 4: Access your app

Once restarted, your app will be accessible at:

```
https://<app-id>.studio.<region>.sagemaker.aws/jupyterlab/default/flask/
```

---

## Comparison

| Feature                        | Built-in SageMaker Proxy | Jupyter Server Proxy       |
|-------------------------------|--------------------------|----------------------------|
| Setup required                | None                     | One-time install + restart |
| Named URL path                | No (port-based)          | Yes (e.g. `/flask/`)       |
| Process lifecycle management  | Manual                   | Managed by extension       |
| AWS documentation             | Limited                  | None (third-party package) |
| Best for                      | Quick testing            | More structured workflows  |

---

## Tips and Troubleshooting

- **500: Internal Server Error** - This almost always means a port mismatch.
  Make sure the port in `app.run(...)`, your proxy config, and your URL all
  match (e.g. all set to `8050`).

- **App not responding** - Check `flask.log` for startup errors. You can view
  it with `cat flask.log` in a terminal or notebook cell.

- **Port already in use** - Kill any existing process on the port before
  starting a new one:
  ```bash
  fuser -k 8050/tcp
  ```

- **Jupyter Server Proxy not working after install** - Make sure you have
  fully restarted the JupyterLab app from the Studio UI (not just the kernel).
  A kernel restart is not sufficient.

---

## Notes

- These approaches work with Amazon SageMaker Studio using JupyterLab apps
  on standard SageMaker AI Studio domains.
- The Jupyter Server Proxy is a third-party open-source package and is not
  an AWS-managed service. Refer to its documentation for advanced
  configuration options.
- Always ensure your Flask app does not expose sensitive data, as the proxy
  URL is accessible to anyone with access to your Studio domain.

---

## References

- Jupyter Server Proxy documentation:
  https://jupyter-server-proxy.readthedocs.io/en/latest/
- Amazon SageMaker Studio documentation:
  https://docs.aws.amazon.com/sagemaker/latest/dg/studio.html
```
