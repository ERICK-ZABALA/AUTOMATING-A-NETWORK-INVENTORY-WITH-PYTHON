# expose internal modules
from .statuses import HealthStatus

# limited the # of exports
# (do not export Null)
__all__ = ['OK', 'WARNING', 'CRITICAL', 'ERRORED', 'PARTIAL']


# create generic status codes
OK      = HealthStatus(0)
WARNING = HealthStatus(1)
CRITICAL= HealthStatus(2)
ERRORED = HealthStatus(3)
PARTIAL = HealthStatus(4)
NULL    = HealthStatus(99)
