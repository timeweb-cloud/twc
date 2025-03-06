"""Timeweb Cloud API client."""

from typing import Optional, Union, List
from uuid import UUID
from pathlib import Path
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network

from .base import TimewebCloudBase
from .types import (
    DNSRecordType,
    ServerConfiguration,
    ServerAction,
    ServerLogOrder,
    ServerBootMode,
    ServerNATMode,
    ServerOSType,
    BackupAction,
    BackupInterval,
    IPVersion,
    ServiceRegion,
    ServiceAvailabilityZone,
    ResourceType,
    DBMS,
    MySQLAuthPlugin,
    LoadBalancerProto,
    LoadBalancerAlgo,
    FirewallProto,
    FirewallDirection,
    FirewallPolicy,
)


class TimewebCloud(TimewebCloudBase):
    """Timeweb Cloud API client class."""

    # -----------------------------------------------------------------------
    # Account

    def get_account_status(self):
        """Return Timeweb Cloud account status."""
        return self._request("GET", f"{self.api_url}/account/status")

    def get_account_finances(self):
        """Return finances."""
        return self._request("GET", f"{self.api_url}/account/finances")

    def get_account_restrictions(self):
        """Return account access restrictions info."""
        return self._request("GET", f"{self.api_url}/auth/access")

    # -----------------------------------------------------------------------
    # Cloud Servers

    def get_servers(self, limit: int = 100, offset: int = 0):
        """Get list of Cloud Server objects."""
        params = {"limit": limit, "offset": offset}
        return self._request("GET", f"{self.api_url}/servers", params=params)

    def get_server(self, server_id: int):
        """Get Cloud Server object."""
        return self._request("GET", f"{self.api_url}/servers/{server_id}")

    def create_server(
        self,
        name: str,
        bandwidth: int,
        configuration: Optional[ServerConfiguration] = None,
        preset_id: Optional[int] = None,
        os_id: Optional[int] = None,
        image_id: Optional[UUID] = None,
        comment: Optional[str] = None,
        avatar_id: Optional[str] = None,
        software_id: Optional[int] = None,
        ssh_keys_ids: Optional[List[int]] = None,
        is_local_network: Optional[bool] = None,  # deprecated
        is_ddos_guard: bool = False,
        network: Optional[dict] = None,
        availability_zone: Optional[ServiceAvailabilityZone] = None,
        is_root_password_required: Optional[bool] = None,
    ):
        """Create new Cloud Server. Note:

        - configuration and preset_id is mutually exclusive.
        - os_id and image_id is mutually exclusive.
        - Location depends on configurator.location or preset.location.
        """
        if not configuration and not preset_id:
            raise ValueError(
                "One of parameters is required: configuration, preset_id"
            )
        if not os_id and not image_id:
            raise ValueError("One of parameters is required: os_id, image_id")

        payload = {
            "name": name,
            "bandwidth": bandwidth,
            **({"comment": comment} if comment else {}),
            **({"avatar_id": avatar_id} if avatar_id else {}),
            **({"software_id": software_id} if software_id else {}),
            **({"ssh_keys_ids": ssh_keys_ids} if ssh_keys_ids else {}),
            "is_ddos_guard": is_ddos_guard,
            **(
                {"is_local_network": is_local_network}
                if is_local_network is not None
                else {}
            ),
            **({"network": network} if network else {}),
            **({"configuration": configuration} if configuration else {}),
            **({"preset_id": preset_id} if preset_id else {}),
            **({"os_id": os_id} if os_id else {}),
            **({"image_id": image_id} if image_id else {}),
            **(
                {"availability_zone": str(availability_zone)}
                if availability_zone
                else {}
            ),
            **(
                {"is_root_password_required": is_root_password_required}
                if is_root_password_required is not None
                else {}
            ),
        }

        return self._request("POST", f"{self.api_url}/servers", json=payload)

    def delete_server(
        self,
        server_id: int,
        delete_hash: Optional[str] = None,
        code: Optional[int] = None,
    ):
        """Delete Cloud Server by ID."""
        params = {
            **({"hash": delete_hash} if delete_hash else {}),
            **({"code": code} if code else {}),
        }
        return self._request(
            "DELETE",
            f"{self.api_url}/servers/{server_id}",
            params=params,
        )

    def update_server(
        self,
        server_id: int,
        name: Optional[str] = None,
        bandwidth: Optional[int] = None,
        configuration: Optional[ServerConfiguration] = None,
        preset_id: Optional[int] = None,
        os_id: Optional[int] = None,
        image_id: Optional[UUID] = None,
        software_id: Optional[int] = None,
        comment: Optional[str] = None,
        avatar_id: Optional[str] = None,
    ):
        """Update Cloud Server. Note:

        - configuration and preset_id is mutually exclusive.
        - os_id and image_id is mutually exclusive.
        """
        payload = {
            **({"name": name} if name else {}),
            **({"bandwidth": bandwidth} if bandwidth else {}),
            # API issue: Non-consistent name: 'configurator' must be named 'configuration'
            **({"configurator": configuration} if configuration else {}),
            **({"preset_id": preset_id} if preset_id else {}),
            **({"os_id": os_id} if os_id else {}),
            **({"image_id": image_id} if image_id else {}),
            **({"software_id": software_id} if software_id else {}),
            **({"comment": comment} if comment else {}),
            **({"avatar_id": avatar_id} if avatar_id else {}),
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/servers/{server_id}",
            json=payload,
        )

    def do_action_with_server(self, server_id: int, action: ServerAction):
        """Do action with Cloud Server. API returns HTTP 204 on success."""
        return self._request(
            "POST",
            f"{self.api_url}/servers/{server_id}/action",
            json={"action": action},
        )

    def clone_server(self, server_id: int):
        """Clone Cloud Server.
        Make copy of existing server and return clone object.
        """
        return self._request(
            "POST", f"{self.api_url}/servers/{server_id}/clone", json={}
        )

    def get_server_preset_types(self):
        """List all available preset and configurator IDs by their types."""
        return self._request("GET", f"{self.api_url}/presets/types/servers")

    def get_server_configurators(self):
        """List configurators."""
        return self._request("GET", f"{self.api_url}/configurator/servers")

    def get_server_presets(self):
        """List available server configuration presets."""
        return self._request("GET", f"{self.api_url}/presets/servers")

    def get_server_os_images(self):
        """List available prebuilt operating system images."""
        return self._request("GET", f"{self.api_url}/os/servers")

    def get_server_software(self):
        """List available software."""
        return self._request("GET", f"{self.api_url}/software/servers")

    def get_server_logs(
        self,
        server_id: int,
        order: ServerLogOrder,
        limit: int = 100,
        offset: int = 0,
    ):
        """View server action logs. Logs can be ordered by datetime."""
        params = {"limit": limit, "offset": offset, "order": order}
        return self._request(
            "GET",
            f"{self.api_url}/servers/{server_id}/logs",
            params=params,
        )

    def set_server_boot_mode(self, server_id: int, boot_mode: ServerBootMode):
        """Change Cloud Server boot mode."""
        if boot_mode == "recovery":
            boot_mode = "recovery_disk"
        return self._request(
            "POST",
            f"{self.api_url}/servers/{server_id}/boot-mode",
            json={"boot_mode": boot_mode},
        )

    def set_server_nat_mode(self, server_id: int, nat_mode: ServerNATMode):
        """Change Cloud Server NAT mode. Available only for servers with LAN."""
        return self._request(
            "PATCH",
            f"{self.api_url}/servers/{server_id}/local-networks/nat-mode",
            json={"nat_mode": nat_mode},
        )

    # -----------------------------------------------------------------------
    # Cloud Servers: Public IPs

    def get_ips(self, server_id: int):
        """Get list of Cloud Server public IPs."""
        return self._request("GET", f"{self.api_url}/servers/{server_id}/ips")

    def add_ip(
        self, server_id: int, version: IPVersion, ptr: Optional[str] = None
    ):
        """Add new public IP to Cloud Server."""
        return self._request(
            "POST",
            f"{self.api_url}/servers/{server_id}/ips",
            json={"type": version, "ptr": ptr},
        )

    def delete_ip(self, server_id: int, ip: Union[IPv4Address, IPv6Address]):
        """Delete IP address from Cloud Server."""
        # pylint: disable=invalid-name
        return self._request(
            "DELETE",
            f"{self.api_url}/servers/{server_id}/ips",
            json={"ip": ip},
        )

    def update_ip(
        self, server_id: int, ptr: str, ip: Union[IPv4Address, IPv6Address]
    ):
        """Update IP address properties."""
        # pylint: disable=invalid-name
        return self._request(
            "PATCH",
            f"{self.api_url}/servers/{server_id}/ips",
            json={"ip": ip, "ptr": ptr},
        )

    # -----------------------------------------------------------------------
    # Cloud Servers: Disks

    def get_disks(self, server_id: int):
        """List Cloud Server disks."""
        return self._request(
            "GET",
            f"{self.api_url}/servers/{server_id}/disks",
        )

    def get_disk(self, server_id: int, disk_id: int):
        """Get disk."""
        return self._request(
            "GET",
            f"{self.api_url}/servers/{server_id}/disks/{disk_id}",
        )

    def add_disk(self, server_id: int, size: int):
        """Add new disk to Cloud Server."""
        return self._request(
            "POST",
            f"{self.api_url}/servers/{server_id}/disks",
            json={"size": size},
        )

    def update_disk(self, server_id: int, disk_id: int, size: int):
        """Resize disk."""
        return self._request(
            "PATCH",
            f"{self.api_url}/servers/{server_id}/disks/{disk_id}",
            json={"size": size},
        )

    def delete_disk(self, server_id: int, disk_id: int):
        """Permanently delete disk. Cannot delete system disk."""
        return self._request(
            "DELETE",
            f"{self.api_url}/servers/{server_id}/disks/{disk_id}",
        )

    def get_disk_autobackup_settings(self, server_id: int, disk_id: int):
        """Return disk auto-backup settings."""
        return self._request(
            "GET",
            f"{self.api_url}/servers/{server_id}/disks/{disk_id}/auto-backups",
        )

    def update_disk_autobackup_settings(
        self,
        server_id: int,
        disk_id: int,
        is_enabled: Optional[bool] = None,
        copy_count: Optional[int] = None,
        creation_start_at: Optional[int] = None,
        interval: Optional[BackupInterval] = None,
        day_of_week: Optional[int] = None,
    ):
        """Update disk auto-backup settings."""
        payload = {
            **({"is_enabled": is_enabled} if is_enabled is not None else {}),
            **({"copy_count": copy_count} if copy_count else {}),
            **(
                {"creation_start_at": creation_start_at}
                if creation_start_at
                else {}
            ),
            **({"interval": interval} if interval else {}),
            **({"day_of_week": day_of_week} if day_of_week else {}),
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/servers/{server_id}/disks/{disk_id}/auto-backups",
            json=payload,
        )

    # -----------------------------------------------------------------------
    # Cloud Servers: Backups

    def get_disk_backups(self, server_id: int, disk_id: int):
        """Get backups list of server disk."""
        return self._request(
            "GET",
            f"{self.api_url}/servers/{server_id}/disks/{disk_id}/backups",
        )

    def get_disk_backup(self, server_id: int, disk_id: int, backup_id: int):
        """Get disk backup."""
        url = (
            f"{self.api_url}/servers/{server_id}"
            + f"/disks/{disk_id}/backups/{backup_id}"
        )
        return self._request("GET", url)

    def create_disk_backup(
        self, server_id: int, disk_id: int, comment: Optional[str] = None
    ):
        """Create new backup."""
        return self._request(
            "POST",
            f"{self.api_url}/servers/{server_id}/disks/{disk_id}/backups",
            json={"comment": comment},
        )

    def update_disk_backup(
        self,
        server_id: int,
        disk_id: int,
        backup_id: int,
        comment: Optional[str] = None,
    ):
        """Update backup properties."""
        url = (
            f"{self.api_url}/servers/{server_id}"
            + f"/disks/{disk_id}/backups/{backup_id}"
        )
        return self._request("PATCH", url, json={"comment": comment})

    def delete_disk_backup(self, server_id: int, disk_id: int, backup_id: int):
        """Delete backup."""
        url = (
            f"{self.api_url}/servers/{server_id}"
            + f"/disks/{disk_id}/backups/{backup_id}"
        )
        return self._request("DELETE", url)

    def do_action_with_disk_backup(
        self,
        server_id: int,
        disk_id: int,
        backup_id: int,
        action: BackupAction,
    ):
        """Perform action with backup."""
        url = (
            f"{self.api_url}/servers/{server_id}"
            + f"/disks/{disk_id}/backups/{backup_id}/action"
        )
        return self._request("POST", url, json={"action": action})

    # -----------------------------------------------------------------------
    # SSH-keys

    def get_ssh_keys(self):
        """Get list of SSH-keys."""
        return self._request("GET", f"{self.api_url}/ssh-keys")

    def get_ssh_key(self, ssh_key_id: int):
        """Get SSH-key by ID."""
        return self._request("GET", f"{self.api_url}/ssh-keys/{ssh_key_id}")

    def add_new_ssh_key(self, name: str, body: str, is_default: bool = False):
        """Add new SSH-key."""
        payload = {"name": name, "body": body, "is_default": is_default}
        return self._request("POST", f"{self.api_url}/ssh-keys", json=payload)

    def update_ssh_key(
        self,
        ssh_key_id: int,
        name: Optional[str] = None,
        body: Optional[str] = None,
        is_default: Optional[bool] = None,
    ):
        """Update an existing SSH-key."""
        payload = {
            **({"name": name} if name else {}),
            **({"body": body} if body else {}),
            **({"is_default": is_default} if is_default is not None else {}),
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/ssh-keys/{ssh_key_id}",
            json=payload,
        )

    def delete_ssh_key(self, ssh_key_id: int):
        """Delete SSH-key by ID."""
        return self._request("DELETE", f"{self.api_url}/ssh-keys/{ssh_key_id}")

    def add_ssh_key_to_server(self, server_id: int, ssh_keys_ids: list):
        """Add SSH-keys to Cloud Server."""
        return self._request(
            "POST",
            f"{self.api_url}/servers/{server_id}/ssh-keys",
            # API issue: Non-consistent name: 'ssh_key_ids' must be named 'ssh_keys_ids'
            json={"ssh_key_ids": ssh_keys_ids},
        )

    def delete_ssh_key_from_server(self, server_id: int, ssh_key_id: int):
        """Delete SSH-key from Cloud Server."""
        return self._request(
            "DELETE",
            f"{self.api_url}/servers/{server_id}/ssh-keys/{ssh_key_id}",
        )

    # -----------------------------------------------------------------------
    # Images

    def get_images(self, limit: int = 100, offset: int = 0):
        """Get list of images."""
        params = {
            "limit": limit,
            "offset": offset,
        }
        return self._request("GET", f"{self.api_url}/images", params=params)

    def get_image(self, image_id: UUID):
        """Get image."""
        return self._request("GET", f"{self.api_url}/images/{image_id}")

    def create_image(
        self,
        disk_id: Optional[int] = None,
        upload_url: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        os_type: Optional[ServerOSType] = None,
        location: Optional[ServiceRegion] = None,
    ):
        """Create disk image. disk_id and upload_url is mutually exclusive.
        disk_id or upload_url is required.
        """
        payload = {
            **({"disk_id": disk_id} if disk_id else {}),
            **({"name": name} if name else {}),
            **({"description": description} if description else {}),
            **({"os": os_type} if os_type else {}),
            **({"location": location} if location else {}),
            **({"upload_url": upload_url} if upload_url else {}),
        }
        return self._request("POST", f"{self.api_url}/images", json=payload)

    def update_image(
        self,
        image_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Update image properties."""
        payload = {
            **({"name": name} if name else {}),
            **({"description": description} if description else {}),
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/images/{image_id}",
            json=payload,
        )

    def upload_image(self, image_id: UUID, filename: Path):
        """Upload image to storage."""
        self.headers.update({"Content-Type": "multipart/form-data"})
        self.headers.update({"Content-Disposition": filename})
        with open(filename, "rb") as image:
            return self._request(
                "POST",
                f"{self.api_url}/images/{image_id}",
                files={"file": image},
            )

    def delete_image(self, image_id: UUID):
        """Remove image."""
        return self._request("DELETE", f"{self.api_url}/images/{image_id}")

    # -----------------------------------------------------------------------
    # Projects

    def get_projects(self):
        """Get account projects list."""
        return self._request("GET", f"{self.api_url}/projects")

    def get_project(self, project_id: int):
        """Get account project by ID."""
        return self._request("GET", f"{self.api_url}/projects/{project_id}")

    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        avatar_id: Optional[int] = None,
    ):
        """Create project."""
        payload = {
            "name": name,
            "description": description,
            "avatar_id": avatar_id,
        }
        return self._request("POST", f"{self.api_url}/projects", json=payload)

    def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        avatar_id: Optional[int] = None,
    ):
        """Update project properties."""
        payload = {
            **({"name": name} if name else {}),
            **({"description": description} if description else {}),
            **({"avatar_id": avatar_id} if avatar_id else {}),
        }
        return self._request(
            "PUT",
            f"{self.api_url}/projects/{project_id}",
            json=payload,
        )

    def delete_project(self, project_id: int):
        """Delete project by ID."""
        return self._request("DELETE", f"{self.api_url}/projects/{project_id}")

    def move_resource_to_project(
        self,
        from_project: int,
        to_project: int,
        resource_id: int,
        resource_type: ResourceType,
    ):
        """Move resource to project."""
        payload = {
            "to_project": to_project,
            "resource_id": resource_id,
            "resource_type": resource_type,
        }
        return self._request(
            "PUT",
            f"{self.api_url}/projects/{from_project}/resources/transfer",
            json=payload,
        )

    def get_project_resources(self, project_id: int):
        """Get all project resources."""
        return self._request(
            "GET",
            f"{self.api_url}/projects/{project_id}/resources",
        )

    def get_project_balancers(self, project_id: int):
        """List balancers in project by project_id."""
        return self._request(
            "GET",
            f"{self.api_url}/projects/{project_id}/resources/balancers",
        )

    def get_project_buckets(self, project_id: int):
        """List buckets in project by project_id."""
        return self._request(
            "GET",
            f"{self.api_url}/projects/{project_id}/resources/buckets",
        )

    def get_project_clusters(self, project_id: int):
        """List Kubernetes clusters in project by project_id."""
        return self._request(
            "GET",
            f"{self.api_url}/projects/{project_id}/resources/clusters",
        )

    def get_project_databases(self, project_id: int):
        """List managed databases in project by project_id."""
        return self._request(
            "GET",
            f"{self.api_url}/projects/{project_id}/resources/databases",
        )

    def get_project_servers(self, project_id: int):
        """List servers in project by project_id."""
        return self._request(
            "GET",
            f"{self.api_url}/projects/{project_id}/resources/servers",
        )

    def get_project_dedicated_servers(self, project_id: int):
        """List dedicated servers in project by project_id."""
        return self._request(
            "GET",
            f"{self.api_url}/projects/{project_id}/resources/dedicated",
        )

    def add_balancer_to_project(self, resource_id: int, project_id: int):
        """Add load balancer to project."""
        return self._request(
            "POST",
            f"{self.api_url}/projects/{project_id}/resources/balancers",
            json={"resource_id": resource_id},
        )

    def add_bucket_to_project(self, resource_id: int, project_id: int):
        """Add object storage bucket to project."""
        return self._request(
            "POST",
            f"{self.api_url}/projects/{project_id}/resources/buckets",
            json={"resource_id": resource_id},
        )

    def add_cluster_to_project(self, resource_id: int, project_id: int):
        """Add Kubernetes cluster to project."""
        return self._request(
            "POST",
            f"{self.api_url}/projects/{project_id}/resources/clusters",
            json={"resource_id": resource_id},
        )

    def add_server_to_project(self, resource_id: int, project_id: int):
        """Add Cloud Server to project."""
        return self._request(
            "POST",
            f"{self.api_url}/projects/{project_id}/resources/servers",
            json={"resource_id": resource_id},
        )

    def add_database_to_project(self, resource_id: int, project_id: int):
        """Add managed database to project."""
        return self._request(
            "POST",
            f"{self.api_url}/projects/{project_id}/resources/databases",
            json={"resource_id": resource_id},
        )

    def add_dedicated_server_to_project(
        self, resource_id: int, project_id: int
    ):
        """Add dedicated server to project."""
        return self._request(
            "POST",
            f"{self.api_url}/projects/{project_id}/resources/dedicated",
            json={"resource_id": resource_id},
        )

    # -----------------------------------------------------------------------
    # Managed databases

    def get_databases(self, limit: int = 100, offset: int = 0):
        """Get databases list."""
        params = {"limit": limit, "offset": offset}
        return self._request("GET", f"{self.api_url}/dbs", params=params)

    def get_database(self, db_id: int):
        """Get database."""
        return self._request("GET", f"{self.api_url}/dbs/{db_id}")

    def get_database_presets(self):
        """Get database presets list."""
        return self._request("GET", f"{self.api_url}/presets/dbs")

    def create_database(
        self,
        name: str,
        dbms: DBMS,
        preset_id: int,
        password: str,
        login: Optional[str] = None,
        hash_type: Optional[MySQLAuthPlugin] = None,
        config_parameters: Optional[dict] = None,
    ):
        """Create database."""
        if dbms == "mysql8":
            dbms = "mysql"
        payload = {
            "name": name,
            "type": dbms,
            "login": login,
            "password": password,
            "hash_type": hash_type,
            "preset_id": preset_id,
            "config_parameters": config_parameters,
        }
        return self._request("POST", f"{self.api_url}/dbs", json=payload)

    def update_database(
        self,
        db_id: int,
        name: Optional[str] = None,
        password: Optional[str] = None,
        preset_id: Optional[int] = None,
        config_parameters: Optional[dict] = None,
        external_ip: Optional[bool] = None,
    ):
        """Update database."""
        payload = {
            **({"name": name} if name else {}),
            **({"password": password} if password else {}),
            **({"preset_id": preset_id} if preset_id else {}),
            **(
                {"config_parameters": config_parameters}
                if config_parameters
                else {}
            ),
            **(
                {"is_external_ip": external_ip}
                if external_ip is not None
                else {}
            ),
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/dbs/{db_id}",
            json=payload,
        )

    def delete_database(
        self,
        db_id: int,
        delete_hash: Optional[str] = None,
        code: Optional[int] = None,
    ):
        """Delete database."""
        params = {
            **({"hash": delete_hash} if delete_hash else {}),
            **({"code": code} if code else {}),
        }
        return self._request(
            "DELETE", f"{self.api_url}/dbs/{db_id}", params=params
        )

    def get_database_backups(
        self, db_id: int, limit: int = 100, offset: int = 0
    ):
        """List database backups."""
        return self._request(
            "GET",
            f"{self.api_url}/dbs/{db_id}/backups",
            params={"limit": limit, "offset": offset},
        )

    def get_database_backup(self, db_id: int, backup_id: int):
        """Get database backup."""
        return self._request(
            "GET",
            f"{self.api_url}/dbs/{db_id}/backups/{backup_id}",
        )

    def create_database_backup(self, db_id: int):
        """Create database backup."""
        return self._request(
            "POST",
            f"{self.api_url}/dbs/{db_id}/backups",
            # API issue: Worst design: Send empty JSON for wut?
            json={},
        )

    def delete_database_backup(self, db_id: int, backup_id: int):
        """Delete database backup."""
        return self._request(
            "DELETE",
            f"{self.api_url}/dbs/{db_id}/backups/{backup_id}",
        )

    def restore_database_backup(self, db_id: int, backup_id: int):
        """Restore database backup."""
        return self._request(
            "PUT",
            f"{self.api_url}/dbs/{db_id}/backups/{backup_id}",
        )

    # -----------------------------------------------------------------------
    # Object Storage

    def get_storage_presets(self):
        """Get storage presets list."""
        return self._request("GET", f"{self.api_url}/presets/storages")

    def get_buckets(self):
        """Get buckets list."""
        return self._request("GET", f"{self.api_url}/storages/buckets")

    def create_bucket(
        self, name: str, preset_id: int, is_public: bool = False
    ):
        """Create storage bucket."""
        payload = {
            "name": name,
            "preset_id": preset_id,
            "type": "public" if is_public else "private",
        }
        return self._request(
            "POST",
            f"{self.api_url}/storages/buckets",
            json=payload,
        )

    def delete_bucket(
        self,
        bucket_id: int,
        delete_hash: Optional[str] = None,
        code: Optional[int] = None,
    ):
        """Delete storage bucket."""
        params = {
            **({"hash": delete_hash} if delete_hash else {}),
            **({"code": code} if code else {}),
        }
        return self._request(
            "DELETE",
            f"{self.api_url}/storages/buckets/{bucket_id}",
            params=params,
        )

    def update_bucket(
        self,
        bucket_id: int,
        preset_id: Optional[int] = None,
        is_public: Optional[bool] = None,
    ):
        """Update storage bucket."""
        self.headers.update({"Content-Type": "application/json"})
        payload = {
            **({"preset_id": preset_id} if preset_id else {}),
            **(
                {"bucket_type": "public" if is_public else "private"}
                if is_public is not None
                else {}
            ),
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/storages/buckets/{bucket_id}",
            json=payload,
        )

    def get_storage_users(self):
        """Get storage users list."""
        return self._request("GET", f"{self.api_url}/storages/users")

    def update_storage_user_secret(self, user_id: int, secret_key: str):
        """Update storage user secret key."""
        return self._request(
            "PATCH",
            f"{self.api_url}/storages/users/{user_id}",
            json={"secret_key": secret_key},
        )

    def get_storage_transfer_status(self, bucket_id: int = None):
        """Get storage transfer status."""
        return self._request(
            "GET",
            f"{self.api_url}/storages/buckets/{bucket_id}/transfer-status",
        )

    def start_storage_transfer(
        self,
        src_bucket: str,
        dst_bucket: str,
        access_key: str,
        secret_key: str,
        location: str,
        endpoint: str,
        force_path_style: bool = False,
    ):
        """Start file transfer from any S3-compatible storage to Timeweb Cloud
        Object Storage.
        """
        payload = {
            "access_key": access_key,
            "secret_key": secret_key,
            "location": location,
            "is_force_path_style": force_path_style,
            "endpoint": endpoint,
            "bucket_name": src_bucket,
            "new_bucket_name": dst_bucket,
        }
        return self._request(
            "POST",
            f"{self.api_url}/storages/transfer",
            json=payload,
        )

    def get_bucket_subdomains(self, bucket_id: int = None):
        """Get bucket subdomains list."""
        return self._request(
            "GET",
            f"{self.api_url}/storages/buckets/{bucket_id}/subdomains",
        )

    def add_bucket_subdomains(self, bucket_id: int, subdomains: list):
        """Add subdomains to bucket."""
        return self._request(
            "POST",
            f"{self.api_url}/storages/buckets/{bucket_id}/subdomains",
            json={"subdomains": subdomains},
        )

    def delete_bucket_subdomains(self, bucket_id: int, subdomains: list):
        """Delete bucket subdomains."""
        return self._request(
            "DELETE",
            f"{self.api_url}/storages/buckets/{bucket_id}/subdomains",
            json={"subdomains": subdomains},
        )

    def gen_cert_for_bucket_subdomain(self, subdomain: str):
        """Generate TLS certificate for subdomain attached to bucket."""
        return self._request(
            "POST",
            f"{self.api_url}/storages/certificates/generate",
            json={"subdomain": subdomain},
        )

    # -----------------------------------------------------------------------
    # Load Balancers

    def get_load_balancers(self):
        """Get load balancers list."""
        return self._request("GET", f"{self.api_url}/balancers")

    def get_load_balancer(self, balancer_id: int):
        """Get load balancer."""
        return self._request("GET", f"{self.api_url}/balancers/{balancer_id}")

    def create_load_balancer(
        self,
        name: str,
        preset_id: int,
        algo: LoadBalancerAlgo,
        proto: LoadBalancerProto,
        port: int = 80,
        path: str = "/",
        inter: int = 10,
        timeout: int = 5,
        fall: int = 3,
        rise: int = 2,
        sticky: bool = False,
        proxy_protocol: bool = False,
        force_https: bool = False,
        backend_keepalive: bool = False,
        network: Optional[dict] = None,
    ):
        """Create load balancer."""
        payload = {
            "name": name,
            "preset_id": preset_id,
            "algo": algo,
            "proto": proto,
            "port": port,
            "path": path,
            "inter": inter,
            "timeout": timeout,
            "fall": fall,
            "rise": rise,
            "is_sticky": sticky,
            "is_use_proxy": proxy_protocol,
            "is_ssl": force_https,
            "is_keepalive": backend_keepalive,
            **({"network": network} if network else {}),
        }
        return self._request("POST", f"{self.api_url}/balancers", json=payload)

    def update_load_balancer(
        self,
        balancer_id: int,
        name: Optional[str] = None,
        preset_id: Optional[int] = None,
        algo: Optional[LoadBalancerAlgo] = None,
        proto: Optional[LoadBalancerProto] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
        inter: Optional[int] = None,
        timeout: Optional[int] = None,
        fall: Optional[int] = None,
        rise: Optional[int] = None,
        sticky: Optional[bool] = None,
        proxy_protocol: Optional[bool] = None,
        force_https: Optional[bool] = None,
        backend_keepalive: Optional[bool] = None,
    ):
        """Update load balancer settings."""
        payload = {
            **({"name": name} if name else {}),
            **({"preset_id": preset_id} if preset_id else {}),
            **({"algo": algo} if algo else {}),
            **({"proto": proto} if proto else {}),
            **({"port": port} if port else {}),
            **({"path": path} if path else {}),
            **({"inter": inter} if inter else {}),
            **({"timeout": timeout} if timeout else {}),
            **({"fall": fall} if fall else {}),
            **({"rise": rise} if rise else {}),
            **({"is_sticky": sticky} if sticky is not None else {}),
            **(
                {"is_use_proxy": proxy_protocol}
                if proxy_protocol is not None
                else {}
            ),
            **({"is_ssl": force_https} if force_https is not None else {}),
            **(
                {"is_keepalive": backend_keepalive}
                if backend_keepalive is not None
                else {}
            ),
        }
        return self._request(
            "PATCH", f"{self.api_url}/balancers/{balancer_id}", json=payload
        )

    def delete_load_balancer(
        self,
        balancer_id: int,
        delete_hash: Optional[str] = None,
        code: Optional[int] = None,
    ):
        """Delete load balancer."""
        params = {
            **({"hash": delete_hash} if delete_hash else {}),
            **({"code": code} if code else {}),
        }
        return self._request(
            "DELETE",
            f"{self.api_url}/balancers/{balancer_id}",
            params=params,
        )

    def get_load_balancer_ips(self, balancer_id: int):
        """Get load balancer IP addresses."""
        return self._request(
            "GET", f"{self.api_url}/balancers/{balancer_id}/ips"
        )

    def add_ips_to_load_balancer(self, balancer_id: int, ips: List[str]):
        """Attach IP addresses to load balancer."""
        return self._request(
            "POST",
            f"{self.api_url}/balancers/{balancer_id}/ips",
            json={"ips": ips},
        )

    def delete_ips_from_load_balancer(self, balancer_id: int, ips: List[str]):
        """Detach IP addresses from load balancer."""
        return self._request(
            "DELETE",
            f"{self.api_url}/balancers/{balancer_id}/ips",
            json={"ips": ips},
        )

    def get_load_balancer_rules(self, balancer_id: int):
        """Get load balancer IP addresses."""
        return self._request(
            "GET", f"{self.api_url}/balancers/{balancer_id}/rules"
        )

    def create_load_balancer_rule(
        self,
        balancer_id: int,
        balancer_proto: LoadBalancerProto,
        balancer_port: int,
        server_proto: LoadBalancerProto,
        server_port: int,
    ):
        """Create load balancer rule."""
        payload = {
            "balancer_proto": balancer_proto,
            "balancer_port": balancer_port,
            "server_proto": server_proto,
            "server_port": server_port,
        }
        return self._request(
            "POST",
            f"{self.api_url}/balancers/{balancer_id}/rules",
            json=payload,
        )

    def update_load_balancer_rule(
        self,
        balancer_id: int,
        rule_id: int,
        balancer_proto: Optional[LoadBalancerProto] = None,
        balancer_port: Optional[int] = None,
        server_proto: Optional[LoadBalancerProto] = None,
        server_port: Optional[int] = None,
    ):
        """Create load balancer rule."""
        payload = {
            **({"balancer_proto": balancer_proto} if balancer_proto else {}),
            **({"balancer_port": balancer_port} if balancer_port else {}),
            **({"server_proto": server_proto} if server_proto else {}),
            **({"server_port": server_port} if server_port else {}),
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/balancers/{balancer_id}/rules/{rule_id}",
            json=payload,
        )

    def delete_load_balancer_rule(self, balancer_id: int, rule_id: int):
        """Delete load balancer rule."""
        return self._request(
            "DELETE",
            f"{self.api_url}/balancers/{balancer_id}/rules/{rule_id}",
        )

    def get_load_balancer_presets(self):
        """Get list of LB presets."""
        return self._request("GET", f"{self.api_url}/presets/balancers")

    # -----------------------------------------------------------------------
    # Kubernetes

    def get_k8s_clusters(self, limit: int = 100, offset: int = 0):
        """Get list of Kubernetes clusters."""
        params = {"limit": limit, "offset": offset}
        return self._request(
            "GET",
            f"{self.api_url}/k8s/clusters",
            params=params,
        )

    def get_k8s_cluster(self, cluster_id: int):
        """Get Kubernetes cluster info."""
        return self._request(
            "GET",
            f"{self.api_url}/k8s/clusters/{cluster_id}",
        )

    def create_k8s_cluster(
        self,
        name: str,
        k8s_version: str,
        network_driver: str,
        preset_id: int,
        description: Optional[str] = None,
        ingress: bool = True,
        worker_groups: Optional[list] = None,
    ):
        """Create Kubernetes cluster. Default worker groups::

            [{"name":"default","preset_id":399,"node_count":1}]

        preset_id in worker_groups is worker node preset_id.

        API also have `ha=False` field, but it is not functional. It means
        master node replicas. By default master node have not any replicas.
        """
        payload = {
            "name": name,
            "description": description or "",
            "ha": False,
            "k8s_version": k8s_version,
            "network_driver": network_driver,
            "ingress": ingress,
            "preset_id": preset_id,
            **(
                {"worker_groups": worker_groups}
                if worker_groups is not None
                else {}
            ),
        }
        return self._request(
            "POST",
            f"{self.api_url}/k8s/clusters",
            json=payload,
        )

    def delete_k8s_cluster(
        self,
        cluster_id: int,
        delete_hash: Optional[str] = None,
        code: Optional[int] = None,
    ):
        """Delete Kubernetes cluster."""
        params = {
            **({"hash": delete_hash} if delete_hash else {}),
            **({"code": code} if code else {}),
        }
        return self._request(
            "DELETE",
            f"{self.api_url}/k8s/clusters/{cluster_id}",
            params=params,
        )

    def update_k8s_cluster(self, cluster_id: int, description: str):
        """Update Kubernetes cluster properties."""
        payload = {
            "description": description,
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/k8s/clusters/{cluster_id}",
            json=payload,
        )

    def get_k8s_cluster_resources(self, cluster_id: int):
        """Return cluster resources status."""
        return self._request(
            "GET",
            f"{self.api_url}/k8s/clusters/{cluster_id}/resources",
        )

    def get_k8s_cluster_kubeconfig(self, cluster_id: int):
        """Download kubeconfig for kubecctl util. API respond
        with application/yaml data.
        """
        return self._request(
            "GET",
            f"{self.api_url}/k8s/clusters/{cluster_id}/kubeconfig",
        )

    def get_k8s_node_groups(self, cluster_id: int):
        """Get list of worker nodes groups."""
        return self._request(
            "GET",
            f"{self.api_url}/k8s/clusters/{cluster_id}/groups",
        )

    def get_k8s_node_group(self, cluster_id: int, group_id: int):
        """Get nodes group info."""
        return self._request(
            "GET",
            f"{self.api_url}/k8s/clusters/{cluster_id}/groups/{group_id}",
        )

    def create_k8s_node_group(
        self,
        cluster_id: int,
        name: str,
        preset_id: int,
        node_count: int,
    ):
        """Add new worker nodes group into Kubernetes cluster."""
        payload = {
            "name": name,
            "preset_id": preset_id,
            "node_count": node_count,
        }
        return self._request(
            "POST",
            f"{self.api_url}/k8s/clusters/{cluster_id}/groups",
            json=payload,
        )

    def delete_k8s_node_group(self, cluster_id: int, group_id: int):
        """Delete cluster nodes group."""
        return self._request(
            "DELETE",
            f"{self.api_url}/k8s/clusters/{cluster_id}/groups/{group_id}",
        )

    def get_k8s_nodes_by_group(
        self, cluster_id: int, group_id: int, limit: int = 100, offset: int = 0
    ):
        """Get list of Kubernetes nodes group nodes."""
        params = {"limit": limit, "offset": offset}
        return self._request(
            "GET",
            f"{self.api_url}/k8s/clusters/{cluster_id}/groups/{group_id}/nodes",
            params=params,
        )

    def add_k8s_nodes_to_group(
        self, cluster_id: int, group_id: int, count: int = 0
    ):
        """Add new nodes to nodes group."""
        return self._request(
            "POST",
            f"{self.api_url}/k8s/clusters/{cluster_id}/groups/{group_id}/nodes",
            json={"count": count},
        )

    def delete_k8s_nodes_from_group(
        self, cluster_id: int, group_id: int, count: int = 0
    ):
        """Delete nodes from nodes group."""
        return self._request(
            "DELETE",
            f"{self.api_url}/k8s/clusters/{cluster_id}/groups/{group_id}/nodes",
            json={"count": count},
        )

    def get_k8s_nodes(self, cluster_id: int):
        """Get list of Kubernetes nodes."""
        return self._request(
            "GET",
            f"{self.api_url}/k8s/clusters/{cluster_id}/nodes",
        )

    def delete_k8s_node(self, cluster_id: int, node_id: int):
        """Delete node from cluster."""
        return self._request(
            "DELETE",
            f"{self.api_url}/k8s/clusters/{cluster_id}/nodes/{node_id}",
        )

    def get_k8s_versions(self):
        """List available Kubernetes versions."""
        return self._request("GET", f"{self.api_url}/k8s/k8s_versions")

    def get_k8s_network_drivers(self):
        """List available Kubernetes network drivers."""
        return self._request("GET", f"{self.api_url}/k8s/network_drivers")

    def get_k8s_presets(self):
        """List available Kubernetes nodes presets."""
        return self._request("GET", f"{self.api_url}/presets/k8s")

    # -----------------------------------------------------------------------
    # Domains

    def get_domains(self, limit: int = 100, offset: int = 0):
        """Get domains list."""
        params = {"limit": limit, "offset": offset}
        return self._request("GET", f"{self.api_url}/domains", params=params)

    def get_domain(self, fqdn: str):
        """Get domain."""
        return self._request("GET", f"{self.api_url}/domains/{fqdn}")

    def domain_turn_on_autoprolong(
        self,
        fqdn: str,
        is_autoprolong_enabled: bool = False,
    ):
        """Turn off/on autoprolong domain."""
        payload = {
            "is_autoprolong_enabled": is_autoprolong_enabled,
        }
        return self._request(
            "PATCH", f"{self.api_url}/domains/{fqdn}", json=payload
        )

    def delete_domain(self, fqdn: str):
        """Delete Domain."""
        return self._request("DELETE", f"{self.api_url}/domains/{fqdn}")

    def add_domain(self, fqdn: str):
        """Add Domain."""
        return self._request("POST", f"{self.api_url}/add-domain/{fqdn}")

    def get_domain_dns_records(
        self, fqdn: str, limit: int = 100, offset: int = 0
    ):
        """Get domain DNS records."""
        params = {"limit": limit, "offset": offset}
        return self._request(
            "GET", f"{self.api_url}/domains/{fqdn}/dns-records", params=params
        )

    def add_domain_dns_record(
        self,
        fqdn: str,
        dns_record_type: DNSRecordType,
        value: Optional[str] = None,
        subdomain: Optional[str] = None,
        priority: Optional[int] = None,
        ttl: Optional[int] = None,
        protocol: Optional[str] = None,
        service: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        *,
        null_subdomain: bool = False,
    ):
        """Add DNS record to domain."""
        payload = {
            "type": dns_record_type,
            **({"value": value} if value else {}),
            **({"subdomain": subdomain} if subdomain else {}),
            **({"priority": priority} if priority is not None else {}),
            **({"ttl": ttl} if ttl else {}),
            **({"protocol": protocol} if protocol else {}),
            **({"service": service} if service else {}),
            **({"host": host} if host else {}),
            **({"port": port} if port else {}),
        }
        if null_subdomain:
            payload["subdomain"] = None
        return self._request(
            "POST",
            f"{self.api_url}/domains/{fqdn}/dns-records",
            json=payload,
        )

    def update_domain_dns_record(
        self,
        fqdn: str,
        record_id: int,
        dns_record_type: DNSRecordType,
        value: str,
        subdomain: Optional[str] = None,
        priority: Optional[int] = None,
    ):
        """Update DNS record on domain."""
        payload = {
            "type": dns_record_type,
            "value": value,
            **({"subdomain": subdomain} if subdomain else {}),
            **({"priority": priority} if priority else {}),
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/domains/{fqdn}/dns-records/{record_id}",
            json=payload,
        )

    def delete_domain_dns_record(self, fqdn: str, record_id: int):
        """Delete DNS record on domain."""
        return self._request(
            "DELETE",
            f"{self.api_url}/domains/{fqdn}/dns-records/{record_id}",
        )

    def add_subdomain(self, fqdn: str, subdomain_fqdn: str):
        """Add subdomian tp domain."""
        return self._request(
            "POST",
            f"{self.api_url}/domains/{fqdn}/subdomains/{subdomain_fqdn}",
        )

    def delete_subdomain(self, fqdn: str, subdomain_fqdn: str):
        """Add subdomian tp domain."""
        return self._request(
            "DELETE",
            f"{self.api_url}/domains/{fqdn}/subdomains/{subdomain_fqdn}",
        )

    # -----------------------------------------------------------------------
    # VPC

    # API issue: Why some VPC methods belong to /api/v1 and others to /api/v2??

    def get_vpcs(self):
        """Return list of private networks."""
        return self._request("GET", f"{self.api_url_v2}/vpcs")

    def get_vpc(self, vpc_id: str):
        """Return network information."""
        return self._request("GET", f"{self.api_url_v2}/vpcs/{vpc_id}")

    def create_vpc(
        self,
        name: str,
        subnet: IPv4Network,
        location: ServiceRegion,
        availability_zone: Optional[ServiceAvailabilityZone] = None,
        description: Optional[str] = None,
    ):
        """Create new virtual private network."""
        payload = {
            "name": name,
            "subnet_v4": subnet,
            "location": location,
            **(
                {"availability_zone": str(availability_zone)}
                if availability_zone
                else {}
            ),
            **({"description": description} if description else {}),
        }
        return self._request("POST", f"{self.api_url_v2}/vpcs", json=payload)

    def update_vpc(
        self,
        vpc_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Update network information."""
        payload = {
            **({"name": name} if name else {}),
            **({"description": description} if description else {}),
        }
        return self._request(
            "PATCH",
            f"{self.api_url_v2}/vpcs/{vpc_id}",
            json=payload,
        )

    def delete_vpc(self, vpc_id: str):
        """Delete network."""
        return self._request("DELETE", f"{self.api_url_v1}/vpcs/{vpc_id}")

    def get_services_in_vpc(self, vpc_id: str):
        """Return network information."""
        return self._request(
            "GET", f"{self.api_url_v2}/vpcs/{vpc_id}/services"
        )

    def get_vpc_ports(self, vpc_id: str):
        """Return network information."""
        return self._request("GET", f"{self.api_url_v1}/vpcs/{vpc_id}/ports")

    # -----------------------------------------------------------------------
    # Firewall

    def get_firewall_groups(self, limit: int = 100, offset: int = 0):
        """Get list of firewall groups."""
        params = {"limit": limit, "offset": offset}
        return self._request(
            "GET", f"{self.api_url}/firewall/groups", params=params
        )

    def create_firewall_group(
        self,
        name: str,
        description: Optional[str] = None,
        policy: Optional[FirewallPolicy] = FirewallPolicy.DROP,
    ):
        payload = {
            "name": name,
            **({"description": description} if description else {}),
        }
        return self._request(
            "POST",
            f"{self.api_url}/firewall/groups",
            json=payload,
            params={"policy": policy},
        )

    def get_firewall_group(self, group_id: UUID):
        return self._request(
            "GET", f"{self.api_url}/firewall/groups/{group_id}"
        )

    def delete_firewall_group(self, group_id: UUID):
        return self._request(
            "DELETE", f"{self.api_url}/firewall/groups/{group_id}"
        )

    def update_firewall_group(
        self,
        group_id: UUID,
        name: str,
        description: Optional[str] = None,
    ):
        payload = {
            "name": name,
            **({"description": description} if description else {}),
        }
        return self._request(
            "PATCH", f"{self.api_url}/firewall/groups/{group_id}", json=payload
        )

    def get_firewall_group_resources(
        self, group_id: UUID, limit: int = 100, offset: int = 0
    ):
        params = {"limit": limit, "offset": offset}
        return self._request(
            "GET",
            f"{self.api_url}/firewall/groups/{group_id}/resources",
            params=params,
        )

    def link_resource_to_firewall(
        self,
        group_id: UUID,
        resource_id: Union[str, int],
        resource_type: str,
    ):
        if resource_type not in ["server", "dbaas", "balancer"]:
            raise ValueError("Invalid resource type")
        return self._request(
            "POST",
            f"{self.api_url}/firewall/groups/{group_id}/resources/{resource_id}",
            params={"resource_type": resource_type},
        )

    def unlink_resource_from_firewall(
        self,
        group_id: UUID,
        resource_id: Union[str, int],
        resource_type: str,
    ):
        if resource_type not in ["server", "dbaas", "balancer"]:
            raise ValueError("Invalid resource type")
        return self._request(
            "DELETE",
            f"{self.api_url}/firewall/groups/{group_id}/resources/{resource_id}",
            params={"resource_type": resource_type},
        )

    def get_firewall_rules(
        self, group_id: UUID, limit: int = 100, offset: int = 0
    ):
        """Get list of firewall rules."""
        params = {"limit": limit, "offset": offset}
        return self._request(
            "GET",
            f"{self.api_url}/firewall/groups/{group_id}/rules",
            params=params,
        )

    def create_firewall_rule(
        self,
        group_id: UUID,
        direction: FirewallDirection,
        protocol: FirewallProto,
        cidr: Union[IPv4Network, IPv6Network],
        port: Optional[str] = None,
        description: Optional[str] = None,
    ):
        payload = {
            **({"description": description} if description else {}),
            **({} if protocol == FirewallProto.ICMP.value else {"port": port}),
            "direction": direction,
            "protocol": protocol,
            "cidr": cidr,
        }
        return self._request(
            "POST",
            f"{self.api_url}/firewall/groups/{group_id}/rules",
            json=payload,
        )

    def get_firewall_rule(self, group_id: UUID, rule_id: UUID):
        return self._request(
            "GET", f"{self.api_url}/firewall/groups/{group_id}/rules/{rule_id}"
        )

    def delete_firewall_rule(self, group_id: UUID, rule_id: UUID):
        return self._request(
            "DELETE",
            f"{self.api_url}/firewall/groups/{group_id}/rules/{rule_id}",
        )

    def update_firewall_rule(
        self,
        group_id: UUID,
        rule_id: UUID,
        direction: FirewallDirection,
        protocol: FirewallProto,
        cidr: Union[IPv4Network, IPv6Network],
        port: Optional[str] = None,
        description: Optional[str] = None,
    ):
        payload = {
            **({"description": description} if description else {}),
            **({} if protocol == FirewallProto.ICMP.value else {"port": port}),
            "direction": direction,
            "protocol": protocol,
            "cidr": cidr,
        }
        return self._request(
            "PATCH",
            f"{self.api_url}/firewall/groups/{group_id}/rules/{rule_id}",
            json=payload,
        )

    def get_resource_firewall_groups(
        self,
        resource_id: Union[int, str],
        resource_type: str,
        limit: int = 100,
        offset: int = 0,
    ):
        params = {"limit": limit, "offset": offset}
        if resource_type not in ["server", "dbaas", "balancer"]:
            raise ValueError("Invalid resource type")
        return self._request(
            "GET",
            f"{self.api_url}/firewall/service/{resource_type}/{resource_id}",
            params=params,
        )

    # -----------------------------------------------------------------------
    # Floating IPs

    def get_floating_ips(self):
        return self._request("GET", f"{self.api_url_v1}/floating-ips")

    def get_floating_ip(self, floating_ip_id: str):
        return self._request(
            "GET", f"{self.api_url_v1}/floating-ips/{floating_ip_id}"
        )

    def create_floating_ip(
        self,
        availability_zone: ServiceAvailabilityZone,
        ddos_protection: bool = False,
    ):
        payload = {
            "is_ddos_guard": ddos_protection,
            "availability_zone": str(availability_zone),
        }
        return self._request(
            "POST", f"{self.api_url_v1}/floating-ips", json=payload
        )

    def update_floating_ip(
        self,
        floating_ip_id: str,
        comment: Optional[str] = None,
        ptr: Optional[str] = None,
    ):
        payload = {}
        if comment:
            payload["comment"] = comment
        if ptr:
            payload["ptr"] = ptr
        return self._request(
            "PATCH",
            f"{self.api_url_v1}/floating-ips/{floating_ip_id}",
            json=payload,
        )

    def delete_floating_ip(self, floating_ip_id: str):
        return self._request(
            "DELETE", f"{self.api_url_v1}/floating-ips/{floating_ip_id}"
        )

    def attach_floating_ip(
        self,
        floating_ip_id: str,
        resource_type: ResourceType,
        resource_id: str,
    ):
        payload = {"resource_type": resource_type, "resource_id": resource_id}
        return self._request(
            "POST",
            f"{self.api_url_v1}/floating-ips/{floating_ip_id}/bind",
            json=payload,
        )

    def detach_floating_ip(self, floating_ip_id: str):
        return self._request(
            "POST", f"{self.api_url_v1}/floating-ips/{floating_ip_id}/unbind"
        )
