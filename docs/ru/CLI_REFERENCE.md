# `twc`

CLI for Timeweb Cloud services.

**Usage**:

```console
$ twc [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show version and exit.
* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `account`: Manage Timeweb Cloud account.
* `apps`: Manage apps.
* `balancer`: Manage load balancers. (aliases: balancers, lb)
* `cluster`: Manage Kubernetes clusters. (aliases: clusters, kubernetes, k8s)
* `config`: Manage CLI configuration.
* `database`: Manage databases. (aliases: databases, db)
* `domain`: Manage domains and DNS records. (aliases: domains, d)
* `firewall`: Manage Cloud Firewall rules and groups. (aliases: fw)
* `image`: Manage disk images. (aliases: images, i)
* `ip`: Manage floating IPs. (aliases: ips)
* `project`: Manage projects. (aliases: projects, p)
* `server`: Manage Cloud Servers. (aliases: servers, s)
* `ssh-key`: Manage SSH-keys. (aliases: ssh-keys, k)
* `storage`: Manage object storage buckets. (aliases: storages, s3)
* `version`: Show version and exit.
* `vpc`: Manage virtual networks. (aliases: vpcs, network, networks)
* `whoami`: Display current login.

## `twc account`

Manage Timeweb Cloud account.

**Usage**:

```console
$ twc account [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `access`: Manage account access restrictions.
* `finances`: Get finances.
* `status`: Display account status.

### `twc account access`

Manage account access restrictions.

**Usage**:

```console
$ twc account access [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `restrictions`: View access restrictions status.

#### `twc account access restrictions`

View access restrictions status.

**Usage**:

```console
$ twc account access restrictions [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--by-ip`: Display IP restrictions.
* `--by-country`: Display country restrictions.
* `--help`: Show this message and exit.

### `twc account finances`

Get finances.

**Usage**:

```console
$ twc account finances [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc account status`

Display account status.

**Usage**:

```console
$ twc account status [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

## `twc apps`

Manage apps.

**Usage**:

```console
$ twc apps [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create app
* `delete`: Delete apps.
* `get`: Get database info.
* `get-repositories`: Get repositories.
* `get-vcs-providers`: Get VCS providers.
* `list`: List apps. (aliases: ls)
* `list-presets`: Get tarifs; backend or frontend

### `twc apps create`

Create app

**Usage**:

```console
$ twc apps create [OPTIONS] YML_CONFIG_PATH
```

**Arguments**:

* `YML_CONFIG_PATH`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--status`: Display status and exit with 0 if status is 'started'.
* `--help`: Show this message and exit.

### `twc apps delete`

Delete apps.

**Usage**:

```console
$ twc apps delete [OPTIONS] APP_ID
```

**Arguments**:

* `APP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc apps get`

Get database info.

**Usage**:

```console
$ twc apps get [OPTIONS] APP_ID
```

**Arguments**:

* `APP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--status`: Display status and exit with 0 if status is 'started'.
* `--help`: Show this message and exit.

### `twc apps get-repositories`

Get repositories.

**Usage**:

```console
$ twc apps get-repositories [OPTIONS] VCS_PROVIDER_ID
```

**Arguments**:

* `VCS_PROVIDER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc apps get-vcs-providers`

Get VCS providers.

**Usage**:

```console
$ twc apps get-vcs-providers [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc apps list`

List apps.

**Usage**:

```console
$ twc apps list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc apps list-presets`

Get tarifs; backend or frontend

**Usage**:

```console
$ twc apps list-presets [OPTIONS] TYPE
```

**Arguments**:

* `TYPE`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

## `twc balancer`

Manage load balancers.

**Usage**:

```console
$ twc balancer [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `backend`: Manage load balancer backend servers. (aliases: backends)
* `create`: Create load balancer.
* `get`: Get load balancer info.
* `list`: List load balancers. (aliases: ls)
* `list-presets`: List configuration presets. (aliases: lp)
* `remove`: Remove load balancer. (aliases: rm)
* `rule`: Manage load balancer rules. (aliases: rules)
* `set`: Change load balancer parameters.

### `twc balancer backend`

Manage load balancer backend servers.

**Usage**:

```console
$ twc balancer backend [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add new backend servers to balancer.
* `list`: List load balancer backends. (aliases: ls)
* `remove`: Remove load balancer backends. (aliases: rm)

#### `twc balancer backend add`

Add new backend servers to balancer.

**Usage**:

```console
$ twc balancer backend add [OPTIONS] BALANCER_ID BACKEND_IP...
```

**Arguments**:

* `BALANCER_ID`: [required]
* `BACKEND_IP...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

#### `twc balancer backend list`

List load balancer backends.

**Usage**:

```console
$ twc balancer backend list [OPTIONS] BALANCER_ID
```

**Arguments**:

* `BALANCER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc balancer backend remove`

Remove load balancer backends.

**Usage**:

```console
$ twc balancer backend remove [OPTIONS] BALANCER_ID BACKEND...
```

**Arguments**:

* `BALANCER_ID`: [required]
* `BACKEND...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc balancer create`

Create load balancer.

**Usage**:

```console
$ twc balancer create [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Load balancer display name.  [required]
* `--desc TEXT`: Load balancer description.
* `--preset-id INTEGER`: Load balancer preset ID.
* `--replicas INTEGER RANGE`: Load balancer replica count. Ignored if --preset-id set.  [default: 1; 1<=x<=2]
* `--algo [roundrobin|leastconn]`: Balancer algorythm.  [default: roundrobin]
* `--port INTEGER`: Load balancer listen port.  [default: 80]
* `--path TEXT`: URL path.  [default: /]
* `--proto [http|http2|https|tcp]`: Health check protocol.  [default: http]
* `--inter INTEGER`: Health checks interval in seconds.  [default: 10]
* `--timeout INTEGER`: Health check timeout in seconds.  [default: 5]
* `--rise INTEGER`: Number of successful health checks to consider backend as operational.  [default: 3]
* `--fall INTEGER`: Number of unsuccessfull health checks to consider backend as dead.  [default: 2]
* `--sticky / --no-sticky`: Stick on client IP.  [default: no-sticky]
* `--proxy-protocol / --no-proxy-protocol`: [default: no-proxy-protocol]
* `--force-https / --no-force-https`: [default: no-force-https]
* `--backend-keepalive / --no-backend-keepalive`: [default: no-backend-keepalive]
* `--max-connections INTEGER`: Backend server's maximum number of concurrent connections.
* `--connect-timeout INTEGER`: Maximum time to wait for a connection attempt to a backend server to succeed.
* `--client-timeout INTEGER`: Maximum inactivity time on the client side.
* `--server-timeout INTEGER`: Maximum time for pending data staying into output buffer.
* `--http-timeout INTEGER`: Maximum allowed time to wait for a complete HTTP request.
* `--project-id INTEGER`: Add load balancer to specific project.
* `--network-id TEXT`: Private network ID.
* `--private-ip TEXT`: Private IPv4 address.
* `--public-ip TEXT`: Public IPv4 address. New address by default.
* `--no-public-ip`: Do not add public IPv4 address.
* `--region REGION`: Region (location).  [default: ru-1]
* `--availability-zone ZONE`: Availability zone.
* `--cert-type [custom|lets_encrypt]`: SSL certificate type. Falls to 'custom' if --cert-data and --cert-key set.
* `--cert-domain TEXT`: Domain name for which the certificate was issued. Note: domain name A-record will set to load balancer's public IP.
* `--cert-data FILENAME`: Fullchain certificate file.
* `--cert-key FILENAME`: Certificate key file.
* `--help`: Show this message and exit.

### `twc balancer get`

Get load balancer info.

**Usage**:

```console
$ twc balancer get [OPTIONS] BALANCER_ID
```

**Arguments**:

* `BALANCER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--status`: Display status and exit with 0 if status is 'started'.
* `--help`: Show this message and exit.

### `twc balancer list`

List load balancers.

**Usage**:

```console
$ twc balancer list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc balancer list-presets`

List configuration presets.

**Usage**:

```console
$ twc balancer list-presets [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--region [ru-1|ru-2|ru-3|kz-1|pl-1|nl-1|de-1]`: Use region (location).
* `--help`: Show this message and exit.

### `twc balancer remove`

Remove load balancer.

**Usage**:

```console
$ twc balancer remove [OPTIONS] BALANCER_ID...
```

**Arguments**:

* `BALANCER_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc balancer rule`

Manage load balancer rules.

**Usage**:

```console
$ twc balancer rule [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add load balancer rule.
* `list`: List load balancer rules. (aliases: ls)
* `remove`: Remove load balancer rule. (aliases: rm)
* `update`: Update load balancer rule. (aliases: upd)

#### `twc balancer rule add`

Add load balancer rule.

**Usage**:

```console
$ twc balancer rule add [OPTIONS] BALANCER_ID
```

**Arguments**:

* `BALANCER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--frontend PORT/PROTO`: Frontend port and protocol.  [required]
* `--backend PORT/PROTO`: Backend port and protocol.  [required]
* `--help`: Show this message and exit.

#### `twc balancer rule list`

List load balancer rules.

**Usage**:

```console
$ twc balancer rule list [OPTIONS] BALANCER_ID
```

**Arguments**:

* `BALANCER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc balancer rule remove`

Remove load balancer rule.

**Usage**:

```console
$ twc balancer rule remove [OPTIONS] RULE_ID...
```

**Arguments**:

* `RULE_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc balancer rule update`

Update load balancer rule.

**Usage**:

```console
$ twc balancer rule update [OPTIONS] RULE_ID
```

**Arguments**:

* `RULE_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--frontend PORT/PROTO`: Frontend port and protocol.
* `--backend PORT/PROTO`: Backend port and protocol.
* `--help`: Show this message and exit.

### `twc balancer set`

Change load balancer parameters.

**Usage**:

```console
$ twc balancer set [OPTIONS] BALANCER_ID
```

**Arguments**:

* `BALANCER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Load balancer display name.
* `--replicas INTEGER RANGE`: Load balancer replica count.  [1<=x<=2]
* `--algo [roundrobin|leastconn]`: Balancer algorythm.
* `--port INTEGER`: Load balancer listen port.
* `--path TEXT`: URL path.
* `--proto [http|http2|https|tcp]`: Health check protocol.
* `--inter INTEGER`: Health checks interval in seconds.
* `--timeout INTEGER`: Health check timeout in seconds.
* `--rise INTEGER`: Number of successful health checks to consider backend as operational.
* `--fall INTEGER`: Number of unsuccessfull health checks to consider backend as dead.
* `--sticky / --no-sticky`: Stick on client IP.
* `--proxy-protocol / --no-proxy-protocol`
* `--force-https / --no-force-https`
* `--backend-keepalive / --no-backend-keepalive`
* `--max-connections INTEGER`: Backend server's maximum number of concurrent connections.
* `--connect-timeout INTEGER`: Maximum time to wait for a connection attempt to a backend server to succeed.
* `--client-timeout INTEGER`: Maximum inactivity time on the client side.
* `--server-timeout INTEGER`: Maximum time for pending data staying into output buffer.
* `--http-timeout INTEGER`: Maximum allowed time to wait for a complete HTTP request.
* `--help`: Show this message and exit.

## `twc cluster`

Manage Kubernetes clusters.

**Usage**:

```console
$ twc cluster [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create Kubernetes cluster.
* `group`: Manage worker node groups. (aliases: groups)
* `kubeconfig`: Download KubeConfig. (aliases: kubecfg, cfg)
* `list`: List Kubernetes clusters. (aliases: ls)
* `list-k8s-versions`: List available Kubernetes versions. (aliases: lv)
* `list-network-drivers`: List available Kubernetes network drivers.
* `list-presets`: List nodes configuration presets. (aliases: lp)
* `node`: Manage worker nodes. (aliases: nodes)
* `remove`: Remove Kubernetes cluster. (aliases: rm)
* `show`: Show cluster resource usage.

### `twc cluster create`

Create Kubernetes cluster.

**Usage**:

```console
$ twc cluster create [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Cluster's display name.  [required]
* `--desc TEXT`: Cluster description.
* `--k8s-version TEXT`: Kubernetes version. See 'twc k8s list-k8s-versions'. Latest by deafult.
* `--master-preset-id INTEGER`: Master node configuration preset. Minimal by default.
* `--network-driver TEXT`: Network driver.  [default: canal]
* `--ingress / --no-ingress`: Enable Nginx ingress.  [default: ingress]
* `--add-worker-group NAME,PRESET_ID,NODE_COUNT`: Add workers node group.
* `--project-id INTEGER`: Add cluster to specific project.
* `--help`: Show this message and exit.

### `twc cluster group`

Manage worker node groups.

**Usage**:

```console
$ twc cluster group [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add new node group.
* `list`: List cluster node groups. (aliases: ls)
* `remove`: Remove node group. (aliases: rm)
* `scale-down`: Remove worker nodes from group.
* `scale-up`: Add worker nodes to group.

#### `twc cluster group add`

Add new node group.

**Usage**:

```console
$ twc cluster group add [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Node group display name.  [required]
* `--preset-id INTEGER`: Nodes configuration preset.  [required]
* `--nodes INTEGER`: Number of nodes in group.  [default: 1]
* `--help`: Show this message and exit.

#### `twc cluster group list`

List cluster node groups.

**Usage**:

```console
$ twc cluster group list [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc cluster group remove`

Remove node group.

**Usage**:

```console
$ twc cluster group remove [OPTIONS] GROUP_ID...
```

**Arguments**:

* `GROUP_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc cluster group scale-down`

Remove worker nodes from group.

**Usage**:

```console
$ twc cluster group scale-down [OPTIONS] GROUP_ID [COUNT]
```

**Arguments**:

* `GROUP_ID`: [required]
* `[COUNT]`: Nodes count.  [default: 1]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc cluster group scale-up`

Add worker nodes to group.

**Usage**:

```console
$ twc cluster group scale-up [OPTIONS] GROUP_ID [COUNT]
```

**Arguments**:

* `GROUP_ID`: [required]
* `[COUNT]`: Nodes count.  [default: 1]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc cluster kubeconfig`

Download KubeConfig.

**Usage**:

```console
$ twc cluster kubeconfig [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--save PATH`: Path to file. NOTE: Existing file will be overwitten.
* `--help`: Show this message and exit.

### `twc cluster list`

List Kubernetes clusters.

**Usage**:

```console
$ twc cluster list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc cluster list-k8s-versions`

List available Kubernetes versions.

**Usage**:

```console
$ twc cluster list-k8s-versions [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc cluster list-network-drivers`

List available Kubernetes network drivers.

**Usage**:

```console
$ twc cluster list-network-drivers [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc cluster list-presets`

List nodes configuration presets.

**Usage**:

```console
$ twc cluster list-presets [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc cluster node`

Manage worker nodes.

**Usage**:

```console
$ twc cluster node [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List cluster node groups. (aliases: ls)
* `remove`: Remove nodes from cluster. (aliases: rm)

#### `twc cluster node list`

List cluster node groups.

**Usage**:

```console
$ twc cluster node list [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc cluster node remove`

Remove nodes from cluster.

**Usage**:

```console
$ twc cluster node remove [OPTIONS] CLUSTER_ID NODE_ID...
```

**Arguments**:

* `CLUSTER_ID`: [required]
* `NODE_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc cluster remove`

Remove Kubernetes cluster.

**Usage**:

```console
$ twc cluster remove [OPTIONS] CLUSTER_ID...
```

**Arguments**:

* `CLUSTER_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc cluster show`

Show cluster resource usage.

**Usage**:

```console
$ twc cluster show [OPTIONS] CLUSTER_ID
```

**Arguments**:

* `CLUSTER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

## `twc config`

Manage CLI configuration.

**Usage**:

```console
$ twc config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `dump`: Dump configuration.
* `edit`: Open configuration file in default editor.
* `file`: Print config file path.
* `init`: Make new configuration file if not exist...
* `profiles`: Display configuration profiles.
* `set`: Set config parameters.
* `unset`: Unset config parameters.

### `twc config dump`

Dump configuration.

**Usage**:

```console
$ twc config dump [OPTIONS]
```

**Options**:

* `-p, --profile NAME`: Use profile.
* `-o, --output [toml|yaml|json]`: Output format.  [default: toml]
* `--full`: Dump full configuration.
* `--help`: Show this message and exit.

### `twc config edit`

Open configuration file in default editor.

**Usage**:

```console
$ twc config edit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `twc config file`

Print config file path.

**Usage**:

```console
$ twc config file [OPTIONS]
```

**Options**:

* `--locate`: Open file directory in file manager.
* `--help`: Show this message and exit.

### `twc config init`

Make new configuration file if not exist or edit existing.

**Usage**:

```console
$ twc config init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `twc config profiles`

Display configuration profiles.

**Usage**:

```console
$ twc config profiles [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `twc config set`

Set config parameters.

**Usage**:

```console
$ twc config set [OPTIONS] PARAMS...
```

**Arguments**:

* `PARAMS...`: List of KEY=VALUE parameters.  [required]

**Options**:

* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

### `twc config unset`

Unset config parameters.

**Usage**:

```console
$ twc config unset [OPTIONS] PARAMS...
```

**Arguments**:

* `PARAMS...`: List of parameters.  [required]

**Options**:

* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

## `twc database`

Manage databases.

**Usage**:

```console
$ twc database [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `backup`: Manage database backups.
* `create`: Create managed database cluster.
* `get`: Get database info.
* `instance`: Manage instances in cluster (databases/topics/etc). (aliases: db)
* `list`: List databases. (aliases: ls)
* `list-presets`: List database configuration presets. (aliases: lp)
* `list-types`: List database configuration presets. (aliases: lt)
* `remove`: Remove database. (aliases: rm)
* `set`: Set database properties and parameters.
* `user`: Manage database users.

### `twc database backup`

Manage database backups.

**Usage**:

```console
$ twc database backup [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Backup database.
* `list`: List backups. (aliases: ls)
* `remove`: Remove backup. (aliases: rm)
* `restore`: Restore backup.
* `schedule`: Manage database cluster automatic backup...

#### `twc database backup create`

Backup database.

**Usage**:

```console
$ twc database backup create [OPTIONS] DB_ID
```

**Arguments**:

* `DB_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc database backup list`

List backups.

**Usage**:

```console
$ twc database backup list [OPTIONS] DB_ID
```

**Arguments**:

* `DB_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc database backup remove`

Remove backup.

**Usage**:

```console
$ twc database backup remove [OPTIONS] DB_ID BACKUP_ID
```

**Arguments**:

* `DB_ID`: [required]
* `BACKUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc database backup restore`

Restore backup.

**Usage**:

```console
$ twc database backup restore [OPTIONS] DB_ID BACKUP_ID
```

**Arguments**:

* `DB_ID`: [required]
* `BACKUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc database backup schedule`

Manage database cluster automatic backup settings.

**Usage**:

```console
$ twc database backup schedule [OPTIONS] DB_ID
```

**Arguments**:

* `DB_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--status`: Display automatic backups status.
* `--enable / --disable`: Enable or disable automatic backups.
* `--keep INTEGER`: Number of backups to keep.  [default: 1]
* `--start-date [%Y-%m-%d]`: Start date of the first backup creation [default: today].
* `--interval [day|week|month]`: Backup interval.  [default: day]
* `--day-of-week INTEGER RANGE`: The day of the week on which backups will be created. NOTE: This option works only with interval 'week'. First day of week is monday.  [default: 1; 1<=x<=7]
* `--help`: Show this message and exit.

### `twc database create`

Create managed database cluster.

**Usage**:

```console
$ twc database create [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--availability-zone ZONE`: Availability zone.
* `--preset-id INTEGER`: Database configuration preset.  [required]
* `--type TEXT`: Database management system. See TYPE in `twc database list-types`.  [required]
* `--hash-type [caching_sha2|mysql_native]`: Authentication plugin for MySQL.  [default: caching_sha2]
* `--name TEXT`: Database cluster display name.  [required]
* `--param PARAM=VALUE`: Database config parameters, can be multiple.
* `--user-login TEXT`: User login.
* `--user-password TEXT`: User password.
* `--user-host TEXT`: User host for MySQL, Postgres  [default: %]
* `--user-privileges TEXT`: Comma-separated list of user privileges.
* `--user-desc TEXT`: Comment for user.
* `--db-name TEXT`: Database name.
* `--db-desc TEXT`: Database comment.
* `--network-id TEXT`: Private network ID.
* `--private-ip TEXT`: Private IPv4 address.
* `--public-ip TEXT`: Public IPv4 address. New address by default.
* `--no-public-ip`: Do not add public IPv4 address.
* `--project-id INTEGER`: Add database cluster to specific project.
* `--enable-backups`: Enable atomatic backups of database cluster.
* `--backup-keep INTEGER`: Number of backups to keep.  [default: 1]
* `--backup-start-date [%Y-%m-%d]`: Start date of the first backup creation [default: today].
* `--backup-interval [day|week|month]`: Backup interval.  [default: day]
* `--backup-day-of-week INTEGER RANGE`: The day of the week on which backups will be created. NOTE: This option works only with interval 'week'. First day of week is monday.  [default: 1; 1<=x<=7]
* `--help`: Show this message and exit.

### `twc database get`

Get database info.

**Usage**:

```console
$ twc database get [OPTIONS] DB_ID
```

**Arguments**:

* `DB_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--status`: Display status and exit with 0 if status is 'started'.
* `--help`: Show this message and exit.

### `twc database instance`

Manage instances in cluster (databases/topics/etc).

**Usage**:

```console
$ twc database instance [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create database in database cluster.
* `list`: List databases in database cluster. (aliases: ls)
* `remove`: Delete database from cluster. (aliases: rm)

#### `twc database instance create`

Create database in database cluster.

**Usage**:

```console
$ twc database instance create [OPTIONS] DB_ID NAME
```

**Arguments**:

* `DB_ID`: [required]
* `NAME`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--desc TEXT`: Comment for database.
* `--help`: Show this message and exit.

#### `twc database instance list`

List databases in database cluster.

**Usage**:

```console
$ twc database instance list [OPTIONS] DB_ID
```

**Arguments**:

* `DB_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc database instance remove`

Delete database from cluster.

**Usage**:

```console
$ twc database instance remove [OPTIONS] DB_ID INSTANCE_ID
```

**Arguments**:

* `DB_ID`: [required]
* `INSTANCE_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

### `twc database list`

List databases.

**Usage**:

```console
$ twc database list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--limit INTEGER`: Items to display.  [default: 500]
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc database list-presets`

List database configuration presets.

**Usage**:

```console
$ twc database list-presets [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--region [ru-1|ru-2|ru-3|kz-1|pl-1|nl-1|de-1]`: Use region (location).
* `--help`: Show this message and exit.

### `twc database list-types`

List database configuration presets.

**Usage**:

```console
$ twc database list-types [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc database remove`

Remove database.

**Usage**:

```console
$ twc database remove [OPTIONS] DB_ID...
```

**Arguments**:

* `DB_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc database set`

Set database properties and parameters.

**Usage**:

```console
$ twc database set [OPTIONS] DB_ID
```

**Arguments**:

* `DB_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--preset-id INTEGER`: Database configuration preset.
* `--external-ip / --no-external-ip`: Enable external IPv4 address.  [default: external-ip]
* `--name TEXT`: Database instance display name.
* `--param PARAM=VALUE`: Database parameters, can be multiple.
* `--password TEXT`: Database user password
* `--prompt-password / --no-prompt-password`: Set database user password interactively.  [default: no-prompt-password]
* `--help`: Show this message and exit.

### `twc database user`

Manage database users.

**Usage**:

```console
$ twc database user [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create database users.
* `get`: Get database user.
* `list`: List database users. (aliases: ls)
* `remove`: Delete database user. (aliases: rm)

#### `twc database user create`

Create database users.

**Usage**:

```console
$ twc database user create [OPTIONS] DB_ID
```

**Arguments**:

* `DB_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--login TEXT`: User login.  [required]
* `--password TEXT`: User password.  [required]
* `--host TEXT`: User host for MySQL, Postgres  [default: %]
* `--instance-id INTEGER`: The specific instance ID to which the privileges will be applied. If not specified, the privileges will be applied to all available instances.
* `--privileges TEXT`: Comma-separated list of user privileges.
* `--desc TEXT`: Comment for user.
* `--help`: Show this message and exit.

#### `twc database user get`

Get database user.

**Usage**:

```console
$ twc database user get [OPTIONS] DB_ID USER_ID
```

**Arguments**:

* `DB_ID`: [required]
* `USER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc database user list`

List database users.

**Usage**:

```console
$ twc database user list [OPTIONS] DB_ID
```

**Arguments**:

* `DB_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc database user remove`

Delete database user.

**Usage**:

```console
$ twc database user remove [OPTIONS] DB_ID USER_ID
```

**Arguments**:

* `DB_ID`: [required]
* `USER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

## `twc domain`

Manage domains and DNS records.

**Usage**:

```console
$ twc domain [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add domain to account. (aliases: create)
* `info`: Get domain info.
* `list`: List domains. (aliases: ls)
* `record`: Manage DNS records. (aliases: records, rec)
* `remove`: Remove domain names. (aliases: rm)
* `subdomain`: Manage subdomains. (aliases: subdomains, sub)

### `twc domain add`

Add domain to account.

**Usage**:

```console
$ twc domain add [OPTIONS] DOMAIN_NAME
```

**Arguments**:

* `DOMAIN_NAME`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

### `twc domain info`

Get domain info.

**Usage**:

```console
$ twc domain info [OPTIONS] DOMAIN_NAME
```

**Arguments**:

* `DOMAIN_NAME`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc domain list`

List domains.

**Usage**:

```console
$ twc domain list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `-l, --limit INTEGER`: Number of items to display.  [default: 100]
* `-a, --all`: Show subdomains too.
* `--help`: Show this message and exit.

### `twc domain record`

Manage DNS records.

**Usage**:

```console
$ twc domain record [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add dns record for domain or subdomain. (aliases: create)
* `list`: List DNS-records on domain. (aliases: ls)
* `remove`: Delete one DNS-record on domain. (aliases: rm)
* `update`: Update DNS record. (aliases: upd)

#### `twc domain record add`

Add dns record for domain or subdomain.

**Usage**:

```console
$ twc domain record add [OPTIONS] DOMAIN_NAME
```

**Arguments**:

* `DOMAIN_NAME`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--type TYPE`: [TXT|SRV|CNAME|AAAA|MX|A]  [required]
* `--value TEXT`: Record value. Skip it for SRV records.
* `--prio INTEGER`: Record priority. Supported for MX, SRV records.
* `--service TEXT`: Service for SRV record e.g '_matrix'.
* `--proto [TCP|UDP|TLS]`: Protocol for SRV record.
* `--host TEXT`: Host for SRV record.
* `--port INTEGER RANGE`: Port for SRV record.  [1<=x<=65535]
* `--ttl INTEGER`: Time-To-Live for DNS record.
* `--2ld`: Parse subdomain as 2LD.
* `--help`: Show this message and exit.

#### `twc domain record list`

List DNS-records on domain.

**Usage**:

```console
$ twc domain record list [OPTIONS] DOMAIN_NAME
```

**Arguments**:

* `DOMAIN_NAME`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `-a, --all`: Show subdomain records too.
* `--help`: Show this message and exit.

#### `twc domain record remove`

Delete one DNS-record on domain.

**Usage**:

```console
$ twc domain record remove [OPTIONS] DOMAIN_NAME RECORD_ID
```

**Arguments**:

* `DOMAIN_NAME`: [required]
* `RECORD_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

#### `twc domain record update`

Update DNS record.

**Usage**:

```console
$ twc domain record update [OPTIONS] DOMAIN_NAME RECORD_ID
```

**Arguments**:

* `DOMAIN_NAME`: [required]
* `RECORD_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--type TYPE`: [TXT|SRV|CNAME|AAAA|MX|A]  [required]
* `--value TEXT`: [required]
* `--prio INTEGER`: Record priority. Supported for MX, SRV records.
* `--2ld`: Parse subdomain as 2LD.
* `--help`: Show this message and exit.

### `twc domain remove`

Remove domain names.

**Usage**:

```console
$ twc domain remove [OPTIONS] DOMAIN_NAME...
```

**Arguments**:

* `DOMAIN_NAME...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--force`: Force removal.
* `--help`: Show this message and exit.

### `twc domain subdomain`

Manage subdomains.

**Usage**:

```console
$ twc domain subdomain [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Create subdomain. (aliases: create)
* `remove`: Delete subdomain with they DNS records. (aliases: rm)

#### `twc domain subdomain add`

Create subdomain.

**Usage**:

```console
$ twc domain subdomain add [OPTIONS] FQDN
```

**Arguments**:

* `FQDN`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--2ld`: Parse subdomain as 2LD.
* `--help`: Show this message and exit.

#### `twc domain subdomain remove`

Delete subdomain with they DNS records.

**Usage**:

```console
$ twc domain subdomain remove [OPTIONS] FQDN
```

**Arguments**:

* `FQDN`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--2ld`: Parse subdomain as 2LD.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

## `twc firewall`

Manage Cloud Firewall rules and groups.

**Usage**:

```console
$ twc firewall [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `group`: Manage firewall groups. (aliases: groups)
* `link`: Link rules group to service.
* `rule`: Manage firewall rules. (aliases: rules)
* `show`: Display firewall status.
* `unlink`: Unlink rules group from service.

### `twc firewall group`

Manage firewall groups.

**Usage**:

```console
$ twc firewall group [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create new group of firewall rules.
* `dump`: Dump firewall rules.
* `get`: Get firewall fules group.
* `list`: List groups. (aliases: ls)
* `remove`: Remove rules group. All rules in group will lost. (aliases: rm)
* `restore`: Restore firewall rules group from dump file.
* `set`: Set rules group properties.

#### `twc firewall group create`

Create new group of firewall rules.

**Usage**:

```console
$ twc firewall group create [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Group display name.  [required]
* `--desc TEXT`: Description.
* `--policy [DROP|ACCEPT]`: Default firewall policy  [default: DROP]
* `--help`: Show this message and exit.

#### `twc firewall group dump`

Dump firewall rules.

**Usage**:

```console
$ twc firewall group dump [OPTIONS] GROUP_ID
```

**Arguments**:

* `GROUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

#### `twc firewall group get`

Get firewall fules group.

**Usage**:

```console
$ twc firewall group get [OPTIONS] GROUP_ID
```

**Arguments**:

* `GROUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc firewall group list`

List groups.

**Usage**:

```console
$ twc firewall group list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc firewall group remove`

Remove rules group. All rules in group will lost.

**Usage**:

```console
$ twc firewall group remove [OPTIONS] GROUP_ID...
```

**Arguments**:

* `GROUP_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc firewall group restore`

Restore firewall rules group from dump file.

**Usage**:

```console
$ twc firewall group restore [OPTIONS] GROUP_ID
```

**Arguments**:

* `GROUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --file FILENAME`: Firewall rules dump in JSON format.
* `--rules-only`: Do not restore group name and description.
* `--dry-run`: Does not make any changes.
* `--help`: Show this message and exit.

#### `twc firewall group set`

Set rules group properties.

**Usage**:

```console
$ twc firewall group set [OPTIONS] GROUP_ID
```

**Arguments**:

* `GROUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Group display name
* `--desc TEXT`: Description.
* `--help`: Show this message and exit.

### `twc firewall link`

Link rules group to service.

**Usage**:

```console
$ twc firewall link [OPTIONS] (server|database|balancer) RESOURCE_ID GROUP_ID
```

**Arguments**:

* `(server|database|balancer)`: [required]
* `RESOURCE_ID`: [required]
* `GROUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc firewall rule`

Manage firewall rules.

**Usage**:

```console
$ twc firewall rule [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create new firewall rule. (aliases: add)
* `list`: List rules in group. (aliases: ls)
* `remove`: Remove firewall rule. (aliases: rm)
* `update`: Change firewall rule. (aliases: upd)

#### `twc firewall rule create`

Create new firewall rule.

**Usage**:

```console
$ twc firewall rule create [OPTIONS] [PORT[-PORT]/]PROTO...
```

**Arguments**:

* `[PORT[-PORT]/]PROTO...`: List of port/protocol pairs e.g. 22/TCP, 2000-3000/UDP, ICMP  [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-g, --group UUID`: Firewall rules group UUID.
* `-G, --make-group`: Add rules in new rules group.
* `--group-name TEXT`: Rules group name, can be used with '--make-group'
* `--group-policy [DROP|ACCEPT]`: Default firewall policy, can be used with '--make-group'  [default: DROP]
* `--ingress / --egress`: Traffic direction.  [default: ingress]
* `--cidr IP_NETWORK`: IPv4 or IPv6 CIDR. [default: 0.0.0.0/0 or ::/0]
* `--help`: Show this message and exit.

#### `twc firewall rule list`

List rules in group.

**Usage**:

```console
$ twc firewall rule list [OPTIONS] GROUP_ID
```

**Arguments**:

* `GROUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc firewall rule remove`

Remove firewall rule.

**Usage**:

```console
$ twc firewall rule remove [OPTIONS] RULE_ID...
```

**Arguments**:

* `RULE_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

#### `twc firewall rule update`

Change firewall rule.

**Usage**:

```console
$ twc firewall rule update [OPTIONS] RULE_ID
```

**Arguments**:

* `RULE_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--ingress / --egress`: Traffic direction.
* `--cidr IP_NETWORK`: IPv4 or IPv6 CIDR.
* `--port PORT[-PORT]`: Port or ports range e.g. 22, 2000-3000
* `--proto [tcp|udp|icmp|tcp6|udp6|icmp6]`: Protocol.
* `--help`: Show this message and exit.

### `twc firewall show`

Display firewall status.

**Usage**:

```console
$ twc firewall show [OPTIONS] (server|database|balancer|all) [RESOURCE_ID]
```

**Arguments**:

* `(server|database|balancer|all)`: [default: all]
* `[RESOURCE_ID]`

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc firewall unlink`

Unlink rules group from service.

**Usage**:

```console
$ twc firewall unlink [OPTIONS] (server|database|balancer) RESOURCE_ID [GROUP_ID]
```

**Arguments**:

* `(server|database|balancer)`: [required]
* `RESOURCE_ID`: [required]
* `[GROUP_ID]`

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-a, --all`: Unlink all linked firewall groups.
* `--help`: Show this message and exit.

## `twc image`

Manage disk images.

**Usage**:

```console
$ twc image [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create image from existing Cloud Server disk.
* `get`: Get image info.
* `list`: List images. (aliases: ls)
* `remove`: Remove image. (aliases: rm)
* `set`: Change image name and description.
* `upload`: Upload image from URL.

### `twc image create`

Create image from existing Cloud Server disk.

**Usage**:

```console
$ twc image create [OPTIONS] DISK_ID
```

**Arguments**:

* `DISK_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Image human readable name.
* `--desc TEXT`: Image description.
* `--help`: Show this message and exit.

### `twc image get`

Get image info.

**Usage**:

```console
$ twc image get [OPTIONS] IMAGE_ID
```

**Arguments**:

* `IMAGE_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--status`: Display status and exit with 0 if status is 'created'.
* `--help`: Show this message and exit.

### `twc image list`

List images.

**Usage**:

```console
$ twc image list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--limit INTEGER`: Items to display.  [default: 500]
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc image remove`

Remove image.

**Usage**:

```console
$ twc image remove [OPTIONS] IMAGE_ID...
```

**Arguments**:

* `IMAGE_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc image set`

Change image name and description.

**Usage**:

```console
$ twc image set [OPTIONS] IMAGE_ID
```

**Arguments**:

* `IMAGE_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Image human readable name.
* `--desc TEXT`: Image description.
* `--help`: Show this message and exit.

### `twc image upload`

Upload image from URL.

**Usage**:

```console
$ twc image upload [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Direct HTTP(S) link to image.  [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Image human readable name.
* `--desc TEXT`: Image description.
* `--os-type OS_TYPE`: OS type. This value is formal and not affects on server/image.  [default: other]
* `--region REGION`: Region (location).  [default: ru-1]
* `--help`: Show this message and exit.

## `twc ip`

Manage floating IPs.

**Usage**:

```console
$ twc ip [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `attach`: Attach floating IP to service.
* `create`: Create new floating IP.
* `detach`: Detach floating IP from service.
* `get`: Get floating IP.
* `list`: List floating IPs. (aliases: ls)
* `remove`: Remove floating IPs. (aliases: rm)
* `set`: Set floating IP parameters.

### `twc ip attach`

Attach floating IP to service.

**Usage**:

```console
$ twc ip attach [OPTIONS] IP
```

**Arguments**:

* `IP`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--server INTEGER`: Attach IP to Cloud Server.
* `--balancer INTEGER`: Attach IP to Load Balancer.
* `--database INTEGER`: Attach IP to managed database cluster.
* `--help`: Show this message and exit.

### `twc ip create`

Create new floating IP.

**Usage**:

```console
$ twc ip create [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--availability-zone ZONE`: Availability zone.  [required]
* `--ddos-protection`: Request IP-address with L3/L4 DDoS protection.
* `--help`: Show this message and exit.

### `twc ip detach`

Detach floating IP from service.

**Usage**:

```console
$ twc ip detach [OPTIONS] IP
```

**Arguments**:

* `IP`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

### `twc ip get`

Get floating IP.

**Usage**:

```console
$ twc ip get [OPTIONS] IP
```

**Arguments**:

* `IP`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc ip list`

List floating IPs.

**Usage**:

```console
$ twc ip list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc ip remove`

Remove floating IPs.

**Usage**:

```console
$ twc ip remove [OPTIONS] IP...
```

**Arguments**:

* `IP...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc ip set`

Set floating IP parameters.

**Usage**:

```console
$ twc ip set [OPTIONS] IP
```

**Arguments**:

* `IP`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--comment TEXT`: Set comment.
* `--ptr TEXT`: Set reverse DNS pointer.
* `--help`: Show this message and exit.

## `twc project`

Manage projects.

**Usage**:

```console
$ twc project [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create project.
* `list`: List Projects. (aliases: ls)
* `remove`: Remove project. Not affects on project resources. (aliases: rm)
* `resource`: Manage Project resources. (aliases: rsrc)
* `set`: Change proejct name, description and avatar.

### `twc project create`

Create project.

**Usage**:

```console
$ twc project create [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Project display name.
* `--desc TEXT`: Project description.
* `--avatar-id TEXT`: Avatar ID.
* `--help`: Show this message and exit.

### `twc project list`

List Projects.

**Usage**:

```console
$ twc project list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc project remove`

Remove project. Not affects on project resources.

**Usage**:

```console
$ twc project remove [OPTIONS] PROJECT_ID...
```

**Arguments**:

* `PROJECT_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc project resource`

Manage Project resources.

**Usage**:

```console
$ twc project resource [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List project resources. (aliases: ls)
* `move`: Move resources between projects. (aliases: mv)

#### `twc project resource list`

List project resources.

**Usage**:

```console
$ twc project resource list [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--type TEXT`: Resource type.
* `--help`: Show this message and exit.

#### `twc project resource move`

Move resources between projects.

**Usage**:

```console
$ twc project resource move [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Destination project ID.  [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--balancer INTEGER`: Move load balancer.
* `--bucket TEXT`: Move object storage bucket.
* `--cluster INTEGER`: Move Kubernetes cluster.
* `--database INTEGER`: Move database.
* `--dedicated INTEGER`: Move dedicated server.
* `--server INTEGER`: Move Cloud Server.
* `--help`: Show this message and exit.

### `twc project set`

Change proejct name, description and avatar.

**Usage**:

```console
$ twc project set [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Project display name.
* `--desc TEXT`: Project description.
* `--avatar-id TEXT`: Avatar ID.
* `--help`: Show this message and exit.

## `twc server`

Manage Cloud Servers.

**Usage**:

```console
$ twc server [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `backup`: Manage Cloud Server disk backups.
* `boot`: Boot Cloud Server. (aliases: start)
* `clone`: Clone Cloud Server.
* `create`: Create Cloud Server.
* `dash`: Open Cloud Server dashboard in web browser.
* `disk`: Manage Cloud Server disks.
* `get`: Get Cloud Server info.
* `history`: View Cloud Server events log.
* `ip`: (Deprecated) Manage public IPs.
* `list`: List Cloud Servers. (aliases: ls)
* `list-configurators`: List Cloud Server configurators (sets of configuration constraints). (aliases: lc)
* `list-os-images`: List prebuilt operating system images. (aliases: li)
* `list-presets`: List configuration presets. (aliases: lp)
* `list-software`: List software. (aliases: lsw)
* `reboot`: Reboot Cloud Server. (aliases: restart)
* `reinstall`: Reinstall OS or software.
* `remove`: Remove Cloud Server. (aliases: rm)
* `reset-root-password`: Reset root user password.
* `resize`: Update vCPUs number, RAM, disk and bandwidth.
* `set`: Set Cloud Server properties.
* `set-boot-mode`: Set Cloud Server boot mode.
* `set-nat-mode`: Set Cloud Server NAT mode.
* `shutdown`: Shutdown Cloud Server. (aliases: stop)
* `vnc`: Open Cloud Server web VNC console in browser.

### `twc server backup`

Manage Cloud Server disk backups.

**Usage**:

```console
$ twc server backup [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create disk backup.
* `get`: Get disk backup info.
* `list`: List backups by disk_id. (aliases: ls)
* `mount`: Attach backup as external drive.
* `remove`: Remove backups. (aliases: rm)
* `restore`: Restore backup.
* `schedule`: Manage disk automatic backup settings.
* `set`: Change backup properties.
* `unmount`: Detach backup from Cloud Server.

#### `twc server backup create`

Create disk backup.

**Usage**:

```console
$ twc server backup create [OPTIONS] DISK_ID
```

**Arguments**:

* `DISK_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--comment TEXT`: Comment.
* `--help`: Show this message and exit.

#### `twc server backup get`

Get disk backup info.

**Usage**:

```console
$ twc server backup get [OPTIONS] DISK_ID BACKUP_ID
```

**Arguments**:

* `DISK_ID`: [required]
* `BACKUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc server backup list`

List backups by disk_id.

**Usage**:

```console
$ twc server backup list [OPTIONS] DISK_ID
```

**Arguments**:

* `DISK_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc server backup mount`

Attach backup as external drive.

**Usage**:

```console
$ twc server backup mount [OPTIONS] DISK_ID BACKUP_ID
```

**Arguments**:

* `DISK_ID`: [required]
* `BACKUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

#### `twc server backup remove`

Remove backups.

**Usage**:

```console
$ twc server backup remove [OPTIONS] DISK_ID BACKUP_ID...
```

**Arguments**:

* `DISK_ID`: [required]
* `BACKUP_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc server backup restore`

Restore backup.

**Usage**:

```console
$ twc server backup restore [OPTIONS] DISK_ID BACKUP_ID
```

**Arguments**:

* `DISK_ID`: [required]
* `BACKUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc server backup schedule`

Manage disk automatic backup settings.

**Usage**:

```console
$ twc server backup schedule [OPTIONS] DISK_ID
```

**Arguments**:

* `DISK_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--status`: Display automatic backups status.
* `--enable / --disable`: Enable or disable automatic backups.
* `--keep INTEGER`: Number of backups to keep.  [default: 1]
* `--start-date [%Y-%m-%d]`: Start date of the first backup creation [default: today].
* `--interval [day|week|month]`: Backup interval.  [default: day]
* `--day-of-week INTEGER RANGE`: The day of the week on which backups will be created. NOTE: This option works only with interval 'week'. First day of week is monday.  [default: 1; 1<=x<=7]
* `--help`: Show this message and exit.

#### `twc server backup set`

Change backup properties.

**Usage**:

```console
$ twc server backup set [OPTIONS] DISK_ID BACKUP_ID
```

**Arguments**:

* `DISK_ID`: [required]
* `BACKUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--comment TEXT`: Comment.
* `--help`: Show this message and exit.

#### `twc server backup unmount`

Detach backup from Cloud Server.

**Usage**:

```console
$ twc server backup unmount [OPTIONS] DISK_ID BACKUP_ID
```

**Arguments**:

* `DISK_ID`: [required]
* `BACKUP_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

### `twc server boot`

Boot Cloud Server.

**Usage**:

```console
$ twc server boot [OPTIONS] SERVER_ID...
```

**Arguments**:

* `SERVER_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

### `twc server clone`

Clone Cloud Server.

**Usage**:

```console
$ twc server clone [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc server create`

Create Cloud Server.

**Usage**:

```console
$ twc server create [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Cloud Server display name.  [required]
* `--comment TEXT`: Comment.
* `--avatar-id TEXT`: Avatar ID.
* `--image TEXT`: OS ID, OS name or image UUID.  [required]
* `--preset-id INTEGER`: Cloud Server configuration preset ID. NOTE: This argument is mutually exclusive with arguments: ['--cpu', '--ram', '--disk', '--gpu'].
* `--configurator-id INTEGER`: ID of configuration constraints set.
* `--type [standard|premium|dedicated-cpu]`: Cloud Server type. Servers with GPU always is 'premium'. This option will be ignored if '--gpu' or '--preset-id' is set.  [default: premium]
* `--cpu INTEGER`: Number of vCPUs.
* `--ram SIZE`: RAM size, e.g. 1024M, 1G.
* `--disk SIZE`: System disk size, e.g. 10240M, 10G.
* `--gpu INTEGER RANGE`: Number of GPUs to attach.  [0<=x<=4]
* `--bandwidth INTEGER`: Network bandwidth.
* `--software-id INTEGER`: Software ID to install.
* `--ssh-key TEXT`: SSH-key file, name or ID. Can be multiple.
* `--user-data FILENAME`: user-data file for cloud-init.
* `--ddos-protection`: Request public IPv4 with L3/L4 DDoS protection.
* `--network-id TEXT`: Private network ID.
* `--private-ip TEXT`: Private IPv4 address.
* `--public-ip TEXT`: Public IPv4 address. New address by default.
* `--no-public-ip`: Do not add public IPv4 address.
* `--nat-mode MODE`: Apply NAT mode.
* `--region REGION`: Region (location).  [default: ru-1]
* `--availability-zone ZONE`: Availability zone.
* `--project-id INTEGER`: Add server to specific project.
* `--disable-ssh-password-auth`: Disable sshd password authentication.
* `--help`: Show this message and exit.

### `twc server dash`

Open Cloud Server dashboard in web browser.

**Usage**:

```console
$ twc server dash [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `--tab / --win`: Open in new tab or new window.  [default: tab]
* `--print`: Print URL instead of opening web browser.
* `--help`: Show this message and exit.

### `twc server disk`

Manage Cloud Server disks.

**Usage**:

```console
$ twc server disk [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Add disk to Cloud Server.
* `get`: Get Cloud Server disk.
* `list`: List Cloud Server disks. (aliases: ls)
* `remove`: Remove disks. (aliases: rm)
* `resize`: Increase disk size.

#### `twc server disk add`

Add disk to Cloud Server.

**Usage**:

```console
$ twc server disk add [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--size SIZE`: Disk size e.g. 50G.  [required]
* `--help`: Show this message and exit.

#### `twc server disk get`

Get Cloud Server disk.

**Usage**:

```console
$ twc server disk get [OPTIONS] DISK_ID
```

**Arguments**:

* `DISK_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc server disk list`

List Cloud Server disks.

**Usage**:

```console
$ twc server disk list [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc server disk remove`

Remove disks.

**Usage**:

```console
$ twc server disk remove [OPTIONS] DISK_ID...
```

**Arguments**:

* `DISK_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc server disk resize`

Increase disk size.

**Usage**:

```console
$ twc server disk resize [OPTIONS] DISK_ID
```

**Arguments**:

* `DISK_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--size SIZE`: Disk size e.g. 50G.  [required]
* `--help`: Show this message and exit.

### `twc server get`

Get Cloud Server info.

**Usage**:

```console
$ twc server get [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--status`: Display status and exit with 0 if status is 'on'.
* `--networks`: Display networks.
* `--disks`: Display disks.
* `--help`: Show this message and exit.

### `twc server history`

View Cloud Server events log.

**Usage**:

```console
$ twc server history [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--limit INTEGER`: Items to display.  [default: 500]
* `--order [asc|desc]`: Sort log by datetime.  [default: asc]
* `--help`: Show this message and exit.

### `twc server ip`

Manage public IPs.

**Usage**:

```console
$ twc server ip [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Attach new IP to Cloud Server.
* `list`: List public IPs attached to Cloud Server. (aliases: ls)
* `remove`: Remove IP address. (aliases: rm)
* `set`: Set IP pointer (RDNS).

#### `twc server ip add`

Attach new IP to Cloud Server.

**Usage**:

```console
$ twc server ip add [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--ptr POINTER`: IP address pointer (RDNS).
* `--ipv4 / --ipv6`: IP version.  [default: ipv4]
* `--help`: Show this message and exit.

#### `twc server ip list`

List public IPs attached to Cloud Server.

**Usage**:

```console
$ twc server ip list [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc server ip remove`

Remove IP address.

**Usage**:

```console
$ twc server ip remove [OPTIONS] IP_ADDRESS
```

**Arguments**:

* `IP_ADDRESS`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

#### `twc server ip set`

Set IP pointer (RDNS).

**Usage**:

```console
$ twc server ip set [OPTIONS] IP_ADDRESS
```

**Arguments**:

* `IP_ADDRESS`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--ptr POINTER`: IP address pointer (RDNS).
* `--help`: Show this message and exit.

### `twc server list`

List Cloud Servers.

**Usage**:

```console
$ twc server list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--limit INTEGER`: Items to display.  [default: 500]
* `--ids / --no-ids`: Print only server IDs.  [default: no-ids]
* `--help`: Show this message and exit.

### `twc server list-configurators`

List Cloud Server configurators (sets of configuration constraints).

**Usage**:

```console
$ twc server list-configurators [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--region [ru-1|ru-2|ru-3|kz-1|pl-1|nl-1|de-1]`: Use region (location).
* `--help`: Show this message and exit.

### `twc server list-os-images`

List prebuilt operating system images.

**Usage**:

```console
$ twc server list-os-images [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc server list-presets`

List configuration presets.

**Usage**:

```console
$ twc server list-presets [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--region [ru-1|ru-2|ru-3|kz-1|pl-1|nl-1|de-1]`: Use region (location).
* `--help`: Show this message and exit.

### `twc server list-software`

List software.

**Usage**:

```console
$ twc server list-software [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc server reboot`

Reboot Cloud Server.

**Usage**:

```console
$ twc server reboot [OPTIONS] SERVER_ID...
```

**Arguments**:

* `SERVER_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--hard`: Do hard reboot.
* `--help`: Show this message and exit.

### `twc server reinstall`

Reinstall OS or software.

**Usage**:

```console
$ twc server reinstall [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--image TEXT`: OS ID, OS name or image UUID.
* `--software-id INTEGER`: Software ID to install.
* `--add-ssh-keys`: Readd SSH-keys to reinstalled server.  [default: True]
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc server remove`

Remove Cloud Server.

**Usage**:

```console
$ twc server remove [OPTIONS] SERVER_ID...
```

**Arguments**:

* `SERVER_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--keep-public-ip`: Do not remove public IP attached to server. [default: false]
* `--help`: Show this message and exit.

### `twc server reset-root-password`

Reset root user password.

**Usage**:

```console
$ twc server reset-root-password [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc server resize`

Update vCPUs number, RAM, disk and bandwidth.

**Usage**:

```console
$ twc server resize [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--preset-id INTEGER`: Cloud Server configuration preset ID. NOTE: This argument is mutually exclusive with arguments: ['--cpu', '--ram', '--disk'].
* `--cpu INTEGER`: Number of vCPUs.
* `--ram SIZE`: RAM size, e.g. 1024M, 1G.
* `--disk SIZE`: System disk size, e.g. 10240M, 10G.
* `--bandwidth INTEGER`: Network bandwidth.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc server set`

Set Cloud Server properties.

**Usage**:

```console
$ twc server set [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Cloud Server display name.
* `--comment TEXT`: Comment.
* `--avatar-id TEXT`: Avatar ID.
* `--help`: Show this message and exit.

### `twc server set-boot-mode`

Set Cloud Server boot mode.

**Usage**:

```console
$ twc server set-boot-mode [OPTIONS] SERVER_ID... MODE
```

**Arguments**:

* `SERVER_ID...`: Cloud Server ID, Can be multiple.  [required]
* `MODE`: Boot mode: [default|single|recovery]  [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc server set-nat-mode`

Set Cloud Server NAT mode.

**Usage**:

```console
$ twc server set-nat-mode [OPTIONS] SERVER_ID... MODE
```

**Arguments**:

* `SERVER_ID...`: Cloud Server ID, can be multiple.  [required]
* `MODE`: NAT mode: [dnat_and_snat|snat|no_nat]  [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

### `twc server shutdown`

Shutdown Cloud Server.

**Usage**:

```console
$ twc server shutdown [OPTIONS] SERVER_ID...
```

**Arguments**:

* `SERVER_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--hard`: Do hard shutdown.
* `--help`: Show this message and exit.

### `twc server vnc`

Open Cloud Server web VNC console in browser.

**Usage**:

```console
$ twc server vnc [OPTIONS] SERVER_ID
```

**Arguments**:

* `SERVER_ID`: [required]

**Options**:

* `--tab / --win`: Open in new tab or new window.  [default: tab]
* `--print`: Print URL instead of opening web browser.
* `--help`: Show this message and exit.

## `twc ssh-key`

Manage SSH-keys.

**Usage**:

```console
$ twc ssh-key [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Copy SSH-keys to Cloud Server. (aliases: copy)
* `edit`: Edit SSH-key and they properties. (aliases: set, update, upd)
* `get`: Get SSH-key by ID.
* `list`: List SSH-keys. (aliases: ls)
* `new`: Upload new SSH-key.
* `remove`: Remove SSH-keys. (aliases: rm)

### `twc ssh-key add`

Copy SSH-keys to Cloud Server.

**Usage**:

```console
$ twc ssh-key add [OPTIONS] SERVER_ID SSH_KEY_ID...
```

**Arguments**:

* `SERVER_ID`: [required]
* `SSH_KEY_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

### `twc ssh-key edit`

Edit SSH-key and they properties.

**Usage**:

```console
$ twc ssh-key edit [OPTIONS] SSH_KEY_ID
```

**Arguments**:

* `SSH_KEY_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: SSH-key display name.
* `--public-key-file FILE`: Public key file.
* `--default`: Set as default key for new Cloud Servers.
* `--help`: Show this message and exit.

### `twc ssh-key get`

Get SSH-key by ID.

**Usage**:

```console
$ twc ssh-key get [OPTIONS] SSH_KEY_ID
```

**Arguments**:

* `SSH_KEY_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc ssh-key list`

List SSH-keys.

**Usage**:

```console
$ twc ssh-key list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

### `twc ssh-key new`

Upload new SSH-key.

**Usage**:

```console
$ twc ssh-key new [OPTIONS] FILE
```

**Arguments**:

* `FILE`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: SSH-key display name.
* `--default`: Set as default key for new Cloud Servers.
* `--help`: Show this message and exit.

### `twc ssh-key remove`

Remove SSH-keys.

**Usage**:

```console
$ twc ssh-key remove [OPTIONS] SSH_KEY_ID...
```

**Arguments**:

* `SSH_KEY_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--from-server SERVER_ID`: Remove SSH-key from server instead of remove key itself.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

## `twc storage`

Manage object storage buckets.

NOTE: TWC CLI does not implement S3-compatible API client, it uses Timeweb
Cloud specific API methods instead. Use third party S3 clients to manage
objects e.g. s3cmd, rclone, etc.

**Usage**:

```console
$ twc storage [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `genconfig`: Generate config file for S3 clients. (aliases: gencfg, cfg)
* `list`: List buckets. (aliases: ls)
* `list-presets`: List Object Storage presets. (aliases: lp)
* `mb`: Make bucket.
* `rb`: Remove bucket.
* `set`: Set bucket parameters and properties.
* `subdomain`: Manage subdomains. (aliases: domain)
* `user`: Manage Object Storage users.

### `twc storage genconfig`

Generate config file for S3 clients.

**Usage**:

```console
$ twc storage genconfig [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--user-id INTEGER`: Object Storage user ID.
* `--client [rclone|s3cmd]`: S3 client.  [required]
* `--save PATH`: Path to file. NOTE: Existing file will be overwitten.
* `--help`: Show this message and exit.

### `twc storage list`

List buckets.

**Usage**:

```console
$ twc storage list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc storage list-presets`

List Object Storage presets.

**Usage**:

```console
$ twc storage list-presets [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--region [ru-1|ru-2|ru-3|kz-1|pl-1|nl-1|de-1]`: Use region (location).
* `--help`: Show this message and exit.

### `twc storage mb`

Make bucket.

NOTE: A unique prefix for the account will be added to the bucket name
e.g. 'my-bucket' will created as 'c7a04e58-my-bucket'. Prefix will not
be added when creating a bucket via S3 clients.

**Usage**:

```console
$ twc storage mb [OPTIONS] BUCKET
```

**Arguments**:

* `BUCKET`: Bucket name.  [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--preset-id INTEGER`: Storage preset.
* `--type [public|private]`: Bucket access policy.  [default: private]
* `--project-id INTEGER`: Add bucket to specific project.
* `--help`: Show this message and exit.

### `twc storage rb`

Remove bucket.

**Usage**:

```console
$ twc storage rb [OPTIONS] BUCKET
```

**Arguments**:

* `BUCKET`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc storage set`

Set bucket parameters and properties.

**Usage**:

```console
$ twc storage set [OPTIONS] BUCKET
```

**Arguments**:

* `BUCKET`: Bucket name.  [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--preset-id INTEGER`: Storage preset.
* `--type [public|private]`: Bucket access policy.
* `--help`: Show this message and exit.

### `twc storage subdomain`

Manage subdomains.

**Usage**:

```console
$ twc storage subdomain [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`: Attach subdomains to bucket.
* `gencert`: Request TLS certificate for subdomains. (aliases: cert)
* `list`: List subdomains attached to bucket. (aliases: ls)
* `remove`: Remove subdomains. (aliases: rm)

#### `twc storage subdomain add`

Attach subdomains to bucket.

**Usage**:

```console
$ twc storage subdomain add [OPTIONS] BUCKET SUBDOMAIN...
```

**Arguments**:

* `BUCKET`: [required]
* `SUBDOMAIN...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc storage subdomain gencert`

Request TLS certificate for subdomains.

**Usage**:

```console
$ twc storage subdomain gencert [OPTIONS] SUBDOMAIN...
```

**Arguments**:

* `SUBDOMAIN...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `--help`: Show this message and exit.

#### `twc storage subdomain list`

List subdomains attached to bucket.

**Usage**:

```console
$ twc storage subdomain list [OPTIONS] BUCKET
```

**Arguments**:

* `BUCKET`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc storage subdomain remove`

Remove subdomains.

**Usage**:

```console
$ twc storage subdomain remove [OPTIONS] BUCKET SUBDOMAIN...
```

**Arguments**:

* `BUCKET`: [required]
* `SUBDOMAIN...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc storage user`

Manage Object Storage users.

**Usage**:

```console
$ twc storage user [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List storage users. (aliases: ls)
* `passwd`: Set new secret_key for storage user.

#### `twc storage user list`

List storage users.

**Usage**:

```console
$ twc storage user list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.

#### `twc storage user passwd`

Set new secret_key for storage user.

**Usage**:

```console
$ twc storage user passwd [OPTIONS] [ACCESS_KEY]
```

**Arguments**:

* `[ACCESS_KEY]`

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--secret-key TEXT`: [required]
* `--help`: Show this message and exit.

## `twc version`

Show version and exit.

**Usage**:

```console
$ twc version [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `twc vpc`

Manage virtual networks.

**Usage**:

```console
$ twc vpc [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create network.
* `list`: List networks. (aliases: ls)
* `port`: Manage network ports. (aliases: ports)
* `remove`: Remove network. (aliases: rm)
* `set`: Set network properties.
* `show`: List resources in network.

### `twc vpc create`

Create network.

**Usage**:

```console
$ twc vpc create [OPTIONS] NETWORK_SUBNET
```

**Arguments**:

* `NETWORK_SUBNET`: IPv4 network CIDR.  [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Network display name.
* `--desc TEXT`: Description.
* `--region REGION`: Region (location).  [default: ru-1]
* `--availability-zone ZONE`: Availability zone.
* `--help`: Show this message and exit.

### `twc vpc list`

List networks.

**Usage**:

```console
$ twc vpc list [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc vpc port`

Manage network ports.

**Usage**:

```console
$ twc vpc port [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List network ports. (aliases: ls)

#### `twc vpc port list`

List network ports.

**Usage**:

```console
$ twc vpc port list [OPTIONS] VPC_ID
```

**Arguments**:

* `VPC_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

### `twc vpc remove`

Remove network.

**Usage**:

```console
$ twc vpc remove [OPTIONS] VPC_ID...
```

**Arguments**:

* `VPC_ID...`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-y, --yes`: Confirm the action without prompting.
* `--help`: Show this message and exit.

### `twc vpc set`

Set network properties.

**Usage**:

```console
$ twc vpc set [OPTIONS] VPC_ID
```

**Arguments**:

* `VPC_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--name TEXT`: Network display name.
* `--desc TEXT`: Description.
* `--help`: Show this message and exit.

### `twc vpc show`

List resources in network.

**Usage**:

```console
$ twc vpc show [OPTIONS] VPC_ID
```

**Arguments**:

* `VPC_ID`: [required]

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `-f, --filter KEY:VALUE`: Filter output.
* `--help`: Show this message and exit.

## `twc whoami`

Display current login.

**Usage**:

```console
$ twc whoami [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--help`: Show this message and exit.


