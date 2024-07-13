"""Custom data types for Timeweb Cloud API entities."""

from typing import TypedDict
from enum import Enum


class ServiceRegion(str, Enum):
    """Locations which TimewebCloud services is presented."""

    RU_1 = "ru-1"
    RU_2 = "ru-2"
    RU_3 = "ru-3"
    PL_1 = "pl-1"
    KZ_1 = "kz-1"
    NL_1 = "nl-1"


class ServerAction(str, Enum):
    """Available actions on Cloud Server."""

    HARD_REBOOT = "hard_reboot"
    HARD_SHUTDOWN = "hard_shutdown"
    INSTALL = "install"
    REBOOT = "reboot"
    REMOVE = "remove"
    RESET_PASSWORD = "reset_password"
    SHUTDOWN = "shutdown"
    START = "start"
    CLONE = "clone"


class ServerLogOrder(str, Enum):
    """Cloud Server events log order options."""

    ASC = "asc"
    DESC = "desc"


class ServerBootMode(str, Enum):
    """Available boot Cloud Server modes. There are:
    - normal boot from system disk
    - boot in single user mode
    - boot from livecd (SystemRescue distribution)
    """

    DEFAULT = "default"
    SINGLE = "single"
    # In API is named "recovery_disk" there is a shortcut for CLI.
    # See TimewebCloud.set_server_boot_mode()
    RECOVERY = "recovery"


class ServerNATMode(str, Enum):
    """Available NAT options for Cloud Server with enabled LAN."""

    DNAT_AND_SNAT = "dnat_and_snat"
    SNAT = "snat"
    NO_NAT = "no_nat"


class IPVersion(str, Enum):
    """Just IP versions."""

    IPV4 = "ipv4"
    IPV6 = "ipv6"


class ServerConfiguration(TypedDict):
    """
    For `confugurator_id` see `get_server_configurators()`. `disk` and
    `ram` must be in megabytes. Values must comply with the configurator
    constraints.
    """

    configurator_id: int
    disk: int
    cpu: int
    ram: int


class ServerOSType(str, Enum):
    """Operating system types used for determine customers image OS."""

    ALMALINUX = "almalinux"
    ARCHLINUX = "archlinux"
    ASTRALINUX = "astralinux"
    BITRIX = "bitrix"
    BRAINYCP = "brainycp"
    CENTOS = "centos"
    CUSTOM_OS = "custom_os"
    DEBIAN = "debian"
    OTHER = "other"
    UBUNTU = "ubuntu"
    WINDOWS = "windows"


class BackupAction(str, Enum):
    """Available actions for Cloud Server backups."""

    RESTORE = "restore"
    MOUNT = "mount"
    UNMOUNT = "unmount"


class BackupInterval(str, Enum):
    """Available schedule options for Cloud Server backups."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class ResourceType(str, Enum):
    """Resource types."""

    SERVER = "server"
    BALANCER = "balancer"
    DATABASE = "database"
    CLUSTER = "kubernetes"
    BUCKET = "storage"
    DEDICATED_SERVER = "dedicated"


class DBMS(str, Enum):
    """Available DBMS in Timeweb Cloud managed databases service."""

    MYSQL_5 = "mysql5"
    MYSQL_8 = "mysql8"
    POSTGRES = "postgres"
    REDIS = "redis"
    MONGODB = "mongodb"


class MySQLAuthPlugin(str, Enum):
    """MySQL auth plugin options in Timeweb Cloud managed databases
    service.
    """

    CACHING_SHA2 = "caching_sha2"
    MYSQL_NATIVE = "mysql_native"


class BucketType(str, Enum):
    """Bucket access policies."""

    PUBLIC = "public"
    PRIVATE = "private"


class LoadBalancerProto(str, Enum):
    """LB supported protocols."""

    HTTP = "http"
    HTTP2 = "http2"
    HTTPS = "https"
    TCP = "tcp"


class LoadBalancerAlgo(str, Enum):
    """LB supported balancing algorythms."""

    ROUND_ROBIN = "roundrobin"
    LEAST_CONNECTIONS = "leastconn"


class DNSRecordType(str, Enum):
    """Type DNS record"""

    TXT = "TXT"
    SRV = "SRV"
    CNAME = "CNAME"
    AAAA = "AAAA"
    MX = "MX"
    A = "A"


class FirewallProto(str, Enum):
    """Protocols supported by Firewall service."""

    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"


class FirewallDirection(str, Enum):
    """Traffic directions for Firewall service."""

    INGRESS = "ingress"
    EGRESS = "egress"
