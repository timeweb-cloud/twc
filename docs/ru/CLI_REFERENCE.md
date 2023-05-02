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
* `config`: Manage CLI configuration.
* `database`: Manage databases. (aliases: databases, db)
* `image`: Manage disk images. (aliases: images, i)
* `project`: Manage projects. (aliases: projects, p)
* `server`: Manage Cloud Servers. (aliases: servers, s)
* `ssh-key`: Manage SSH-keys. (aliases: ssh-keys, k)
* `storage`: Manage object storage buckets. (aliases: storages, s3)
* `version`: Show version and exit.

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
* `create`: Create managed database instance.
* `get`: Get database info.
* `list`: List databases. (aliases: ls)
* `list-presets`: List database configuration presets. (aliases: lp)
* `remove`: Remove database. (aliases: rm)
* `set`: Set database properties and parameters.

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

### `twc database create`

Create managed database instance.

**Usage**:

```console
$ twc database create [OPTIONS]
```

**Options**:

* `-v, --verbose`: Enable verbose mode.
* `-c, --config FILE`: Use config.
* `-p, --profile NAME`: Use profile.
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
* `--preset-id INTEGER`: Database configuration preset.  [required]
* `--type [mysql5|mysql8|postgres|redis|mongodb]`: Database management system.  [required]
* `--hash-type [caching_sha2|mysql_native]`: Authentication plugin for MySQL.  [default: caching_sha2]
* `--name TEXT`: Database instance display name.  [required]
* `--param PARAM=VALUE`: Database parameters, can be multiple.
* `--login TEXT`: Database user login.
* `--password TEXT`: [required]
* `--project-id INTEGER`: Add database to specific project.
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
* `--region [ru-1|ru-2|pl-1|kz-1|nl-1]`: Use region (location).
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
* `--region [ru-1|ru-2|pl-1|kz-1|nl-1]`: Use region (location).
* `--with-deleted`: Show all images including deleted images.
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
* `--region [ru-1|ru-2|pl-1|kz-1|nl-1]`: Region (location) to upload image.  [default: ru-1]
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
* `ip`: Manage public IPs.
* `list`: List Cloud Servers. (aliases: ls)
* `list-os-images`: List prebuilt operating system images. (aliases: li)
* `list-presets`: List configuration presets. (aliases: lp)
* `list-software`: List software. (aliases: lsw)
* `reboot`: Reboot Cloud Server. (aliases: restart)
* `reinstall`: Reinstall OS or software.
* `remove`: Clone Cloud Server. (aliases: rm)
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
* `--preset-id INTEGER`: Cloud Server configuration preset ID. NOTE: This argument is mutually exclusive with arguments: ['--cpu', '--ram', '--disk'].
* `--cpu INTEGER`: Number of vCPUs.
* `--ram SIZE`: RAM size, e.g. 1024M, 1G.
* `--disk SIZE`: System disk size, e.g. 10240M, 10G.
* `--bandwidth INTEGER`: Network bandwidth.
* `--software-id INTEGER`: Software ID to install.
* `--ssh-key TEXT`: SSH-key file, name or ID. Can be multiple.
* `--ddos-protection`: Enable DDoS-Guard.
* `--local-network`: Enable local network.
* `--project-id INTEGER`: Add server to specific project.
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
* `--region [ru-1|ru-2|pl-1|kz-1|nl-1]`: Use region (location).
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

Clone Cloud Server.

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
$ twc ssh-key add [OPTIONS] SSH_KEY_ID... SERVER_ID
```

**Arguments**:

* `SSH_KEY_ID...`: [required]
* `SERVER_ID`: [required]

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
* `--region [ru-1|ru-2|pl-1|kz-1|nl-1]`: Use region (location).
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
$ twc storage subdomain add [OPTIONS] SUBDOMAIN... BUCKET
```

**Arguments**:

* `SUBDOMAIN...`: [required]
* `BUCKET`: [required]

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
* `-o, --output FORMAT`: Output format, one of: [default|raw|json|yaml].
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


