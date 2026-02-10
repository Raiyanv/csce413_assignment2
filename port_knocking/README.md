## Port Knocking Docker errors

### Implemented the server and client but failed at the knocking stage
- Failed to get past the docker issues (port issues)


#### occured after i exposed 7000-9000:7000-9000/udp ports which led to issues like this or the container just hanged
```bash
Successfully built 40aa1adf62b1
Successfully tagged csce413_assignment2_port_knocking:latest
Recreating 2_network_port_knocking ... 

ERROR: for 2_network_port_knocking  'ContainerConfig'

ERROR: for port_knocking  'ContainerConfig'
Traceback (most recent call last):
  File "bin/docker-compose", line 3, in <module>
  File "compose/cli/main.py", line 67, in main
  File "compose/cli/main.py", line 126, in perform_command
  File "compose/cli/main.py", line 1070, in up
  File "compose/cli/main.py", line 1066, in up
  File "compose/project.py", line 648, in up
  File "compose/parallel.py", line 108, in parallel_execute
  File "compose/parallel.py", line 206, in producer
  File "compose/project.py", line 634, in do
  File "compose/service.py", line 579, in execute_convergence_plan
  File "compose/service.py", line 501, in _execute_convergence_recreate
  File "compose/parallel.py", line 108, in parallel_execute
  File "compose/parallel.py", line 206, in producer
  File "compose/service.py", line 494, in recreate
  File "compose/service.py", line 613, in recreate_container
  File "compose/service.py", line 332, in create_container
  File "compose/service.py", line 917, in _get_container_create_options
  File "compose/service.py", line 957, in _build_container_volume_options
  File "compose/service.py", line 1532, in merge_volume_bindings
  File "compose/service.py", line 1562, in get_container_data_volumes
KeyError: 'ContainerConfig'
[606125] Failed to execute script docker-compose
(base) rasvaid@sceptre-ZenBook-Q526FA-Q526FA:~/eight_sem/
```