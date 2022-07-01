# An Exploratory Hack-a-thon Journey for Hack Week Surrounding Power Consumption (Estimation) and Harvester

## What Can Mostly Exist (not while Harvester is virtualized)
- seemingly through Grafana from Harvester Dashboard there is Prometheus's [Node Exporter](https://github.com/prometheus/node_exporter) which "should" capture on "bare-metal" stats of:
    - powersupplyclass
    - rapl
- and possibly can capture through: machine_nvm_avg_power_budget_watts in Machine 

## Goals
- try to integrate with power consumption estimation more seamlessly with the Harvester Dashboard including during virtualization of Harvester, since virtualization of Harvester is still used for testing purposes - as well as making things airgapped friendly

## Relevant Repositories:
- [Scaphandre](https://github.com/hubblo-org/scaphandre) , the tenative open-source tool to implement 
- [PowerTOP](https://github.com/fenrus75/powertop), what was ultimately pivoted to 
- [HackWeek Branch of forked Harvester-Installer](https://github.com/irishgordo/harvester-installer/commit/ea2c3e796f1fe099419db1604902d722611ef010), harvester installer
- [HackWeek Branch of forked Harvester's os2](https://github.com/irishgordo/os2/commit/82e0fc6cc41d134d73f16182e0da3cc5e16d98f6)
- [HackWeek Branch of forked Luet](https://github.com/irishgordo/luet/tree/hack-week-power-consumption-harvester)

## Open-Source Contributions Derived From SUSE Hack Week:
- [Scaphandre Documentation Fix](https://github.com/hubblo-org/scaphandre/pull/183)

## Exploration
### First Phase:
- exploration contained elements of being able to access Grafana, how the data source for Prometheus is set up as well as possiblity of adding other data sources
- wrapping head around the ability to view the Prometheus front-end, which was accomplished by:
    - `kubectl port-forward services/rancher-monitoring-prometheus -n cattle-monitoring-system 9090:9090` where the kubeconfig was from the Harvester instance 
### Second Phase:
- in an attempt to get Scaphandre up-and-running:
    - there were issues running virtualized
    - `--vm` hookins weren't used at first but could of had potential to work latter
    - locally was validating that it did indeed function as intended:

```

./scaphandre stdout -t 15
Scaphandre stdout exporter
Sending ⚡ metrics
Measurement step is: 2s
Host:   0 W
        package         core            uncore
Top 5 consumers:
Power           PID     Exe
No processes found yet or filter returns no value.
------------------------------------------------------------

Host:   38.727421 W
        package         core            uncore
Socket0 38.72742 W |    34.49148 W      0 W

Top 5 consumers:
Power           PID     Exe
0.854281 W      110110  "qemu-system-x86"
0.03164 W       15      "rcu_preempt"
0.03164 W       116     "ksmd"
0.03164 W       2778    "pipewire"
0 W     1       "systemd"
------------------------------------------------------------

Host:   43.004002 W
        package         core            uncore
Socket0 43.004 W |      38.77722 W      0 W

Top 5 consumers:
Power           PID     Exe
21.326044 W     226146  "qemu-system-x86"
0.035191 W      116     "ksmd"
0.035191 W      856     "nvidia-modeset/kthread_q"
0.035191 W      878     "irq/214-nvidia"
0 W     1       "systemd"
------------------------------------------------------------

Host:   39.776504 W
        package         core            uncore
Socket0 39.776505 W |   35.72909 W      0.00024 W

Top 5 consumers:
Power           PID     Exe
20.144323 W     226146  "qemu-system-x86"
0.034142 W      116     "ksmd"
0.034142 W      856     "nvidia-modeset/kthread_q"
0.034142 W      878     "irq/214-nvidia"
0 W     1       "systemd"
------------------------------------------------------------

Host:   36.829839 W
        package         core            uncore
Socket0 36.82984 W |    32.78854 W      0 W

Top 5 consumers:
Power           PID     Exe
18.77042 W      226146  "qemu-system-x86"
0.0948 W        2784    "pipewire-pulse"
0.0474 W        116     "ksmd"
0.0474 W        2778    "pipewire"
0 W     1       "systemd"
------------------------------------------------------------
```

### Third Phase:
- pivioting away from Scaphandre since it seemed to cause more problems was trying another option like `powertop`, yet that would require building a `custom`, `harvester-os` to use for an `.iso` that had the additional linux package baked in:
```
It involves juggling a locally built Go binary of Luet, Harvester-Installer and Harvester/os2:

For Luet: https://github.com/irishgordo/luet/tree/hack-week-power-consumption-harvester (checkout hack-week-power-consuption-harvester branch), then run make

For Harvester/os2: https://github.com/irishgordo/os2/tree/hackweek (checkout hackweek branch, accidentally committed on dev but it's nothing permanent) Then run ./scripts/build - to build it Copy what it gets tagged as when it's done: 

IE: suse-workstation-team-harvester➜ os2 : dev ✘ :✹ ᐅ docker images | grep -ie 'harvester'
(finding one like: rancher/harvester-os                                              ea2c3e7-dirty                  9a124cf89ab5   8 hours ago     1.71GB)

For Harvester-Installer: https://github.com/irishgordo/harvester-installer/tree/hackweek-power-consumption (checkout hackweek-power-consumption) then copy the luet binary that was built directly to the directory. Modify the BASEOS_IMAGE variable's value to be what the harvester-os locally was tagged as. Then run make and it will build everything. It should build the .iso file.

Then that .iso could be used to spin up a VM and it would have the additional packages of these for instance: https://github.com/irishgordo/os2/blob/hackweek/Dockerfile#L108-L114

```
- there were a mix of initial checksum issues, which was resolved just by cancelling out the affect of the checksum utility in Luet.  
- during all this it became aparent that the ability to read power consumption hinged usually/most-usually on things like:
```
suse-workstation-team-harvester➜  harvester-installer : hackweek-power-consumption ✘ :✹✭ ᐅ  tree /sys/class/powercap 
/sys/class/powercap
├── dtpm -> ../../devices/virtual/powercap/dtpm
├── intel-rapl -> ../../devices/virtual/powercap/intel-rapl
├── intel-rapl:0 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:0
├── intel-rapl:0:0 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0
├── intel-rapl:0:1 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:1
├── intel-rapl:1 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:1
├── intel-rapl-mmio -> ../../devices/virtual/powercap/intel-rapl-mmio
└── intel-rapl-mmio:0 -> ../../devices/virtual/powercap/intel-rapl-mmio/intel-rapl-mmio:0

8 directories, 0 files
suse-workstation-team-harvester➜  harvester-installer : hackweek-power-consumption ✘ :✹✭ ᐅ  tree /sys/class/power_supply 
/sys/class/power_supply
├── AC -> ../../devices/LNXSYSTM:00/LNXSYBUS:00/PNP0A08:00/device:1e/PNP0C09:00/ACPI0003:00/power_supply/AC
└── BAT0 -> ../../devices/LNXSYSTM:00/LNXSYBUS:00/PNP0A08:00/device:1e/PNP0C09:00/PNP0C0A:00/power_supply/BAT0

2 directories, 0 files
```
or:
```
suse-workstation-team-harvester➜  harvester-installer : hackweek-power-consumption ✘ :✹✭ ᐅ  sudo lshw -c power
[sudo] password for mike: 
  *-battery                 
       product: 5B10W13959
       vendor: Celxpert
       physical id: 1
       slot: Front
       capacity: 94000mWh
       configuration: voltage=11.5V
```
yet:

running something that is Virtualized `QEMU/KVM` like nature doesn't seem to provide `/sys/class/*` based information on `power_supply`, `powercap`, and some others

This issue has sparked interest in AWS, they have been working on finding solutions for being able to funnel out power consumption on EC2 instances : https://medium.com/teads-engineering/estimating-aws-ec2-instances-power-consumption-c9745e347959#8e6b - but still very much a work in progress on their end as "not all" EC2 instances have support for `rapl` based things.

- the addition of `powertop` to the base image was complete and validated

### Fourth Phase:
- the inital approach was to try to scaffold a docker container to run on the Harvester instance but the lower fruit was to not juggle with nested virtualization
- adding packages of (pretty sure "all" of the packages weren't totally necessary ):
```
    glibc-devel \
    glibc-utils \
    glibc-extra \
    linux-glibc-devel \
    powertop \
    git \
    python3-pip \
    python3-virtualenv \
    curl
```
- with the new `harvester-os` rebuilt, alongside a `docker system prune -af` to clear things up, the `harvester-installer` was able to kick off and build the new `.iso`
- then a sample dataset was grabbed [report.csv](./report.csv) - 'report.csv' served as an example of what `powertop` could collect while running on the virtualized Harvester VM
- after it was gathered it was creating some quick-and-dirty Python to sift through the `.csv`, and also originally attempt to push out to `pushgateway` with Prometheus 
### Fifth Phase:
- getting the code on the VM:
    - cd'ing into the `/tmp`
    - sudo `git clone` -ing down the repo 
    - `sudo su` shifting to `root`
    - `cd`-ing inside the directory
    - `python3 -m venv venv` && `source venv/bin/activate` && `pip install -r the_directory/requirements.txt`
    - then the script can be run via the virtual env's Python with respective PIP packages
- realized the `pushgateway` with `Prometheus` wasn't working out determined to pivot over something else
- added a new data source of `Grafana's Loki` to our `Harvester Grafana` by:
    - following along with the [Install Grafana Loki with Docker or Docker Compose Guide](https://grafana.com/docs/loki/latest/installation/docker/)
    - added datasource into Grafana
- changed up using a `prometheus` based Python client and instead shifted to just sending a raw request
- started shipping payloads like:
```
(venv) testvmharvester:/tmp/harvester-fuel-gauge-mindmap # python powertop-auditor-prometheus/main.py 
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644497", "[INFO] Current Estimated Watts Used: 37.36000000000001"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644533", "[INFO] Current Estimated Watts Used: 36.48"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644568", "[INFO] Current Estimated Watts Used: 34.72"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644603", "[INFO] Current Estimated Watts Used: 36.800000000000004"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644639", "[INFO] Current Estimated Watts Used: 35.52"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644674", "[INFO] Current Estimated Watts Used: 38.07999999999999"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644710", "[INFO] Current Estimated Watts Used: 35.92000000000001"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644745", "[INFO] Current Estimated Watts Used: 37.12"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644781", "[INFO] Current Estimated Watts Used: 35.04"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644816", "[INFO] Current Estimated Watts Used: 39.52"]]}]}
<Response [204]>
<Response [204]>
 the port is sda
 the port is sdb
{"streams": [{"stream": {"host": "temporarytesting", "job": "power_consumption_estimate"}, "values": [["1656644852", "[INFO] Current Estimated Watts Used: 35.92000000000001"]]}]}
<Response [204]>
<Response [204]>

```
- but ultimately there were still some issues connecting the extracted-transformed-and-loaded data from powertop out to Loki in Grafana on local Harvester VM, there are some tangent open issues on GitHub for Loki at this point that may be related to some issues being seen 


### Sixth Phase
- as a quick pivot we attempted to shuffle back to Scaphandre
- the intent was to:
    - install additional packages needed for `harvester-os` (libvirt specifically so that a virtio mount would work) (rebuilding os)
    - enable shared memory for the VM that is running harvester
    - setup a tempfs mount on the host machine that runs the VMs (in this case Harvester is the only VM running)
    - run Scaphandre on the host-mahcine (not the VM) with `qemu` mode as the 'agent'
    - run Scaphandre on the VM (Harvester) as the `client` mode
- we are able to see that sharing the filesystem's `rapl` based information works correctly via:
```
testvmharvester:/tmp # ls -alh /var/scaphandre/
total 0
drwxrwxrwt 4 root root     80 Jul  1 17:20 .
drwxr-xr-x 1 root root    140 Jul  1 22:16 ..
drwxrwxr-x 2 1000 rancher  60 Jul  1 17:20 intel-rapl:0
drwxrwxr-x 2 1000 rancher  40 Jul  1 17:20 intel-rapl:0:0

## and

suse-workstation-team-harvester➜  temp-thing-whatever  ᐅ  ls -alh /var/lib/libvirt/scaphandre/
total 16K
drwxr-xr-x 5 root root 4.0K Jun 30 21:06 .
drwxr-xr-x 8 root root 4.0K Jun 30 21:06 ..
drwxr-xr-x 2 root root 4.0K Jun 30 21:06 intel-rapl:0
drwxr-xr-x 2 root root 4.0K Jun 30 21:06 intel-rapl:0:0
drwxrwxrwt 4 root root   80 Jul  1 10:20 linux2020
suse-workstation-team-harvester➜  temp-thing-whatever  ᐅ  ls -alh /var/lib/libvirt/scaphandre/linux2020 
total 4.0K
drwxrwxrwt 4 root root   80 Jul  1 10:20 .
drwxr-xr-x 5 root root 4.0K Jun 30 21:06 ..
drwxrwxr-x 2 mike mike   60 Jul  1 10:20 intel-rapl:0
drwxrwxr-x 2 mike mike   40 Jul  1 10:20 intel-rapl:0:0

```
- we were able to see that qemu exporter with scaphandre is working appropriately via:
```
suse-workstation-team-harvester➜  release : main ✔ : ᐅ  ./scaphandre qemu
Scaphandre qemu exporter
Sending ⚡ metrics
```
- but when trying to run scaphandre on the guest-vm (Harvester), there are some Rust panics that correlate to some open issues with the open-source project currently:
```
testvmharvester:/tmp # docker run -v /var/scaphandre:/var/scaphandre -v /proc:/proc -e RUST_BACKTRACE=full -ti hubblo/scaphandre --vm prometheus
scaphandre::sensors::powercap_rapl: Powercap_rapl path is: /var/scaphandre
Scaphandre prometheus exporter
Sending ⚡ metrics
Press CTRL-C to stop scaphandre
thread 'main' panicked at 'Trick: if you are running on a vm, do not forget to use --vm parameter invoking scaphandre at the command line', src/sensors/mod.rs:263:18
stack backtrace:
   0:     0x55a1616f8c70 - std::backtrace_rs::backtrace::libunwind::trace::h72c2fb8038f1bbee
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/../../backtrace/src/backtrace/libunwind.rs:96
   1:     0x55a1616f8c70 - std::backtrace_rs::backtrace::trace_unsynchronized::h1e3b084883f1e78c
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/../../backtrace/src/backtrace/mod.rs:66
   2:     0x55a1616f8c70 - std::sys_common::backtrace::_print_fmt::h3bf6a7ebf7f0394a
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/sys_common/backtrace.rs:79
   3:     0x55a1616f8c70 - <std::sys_common::backtrace::_print::DisplayBacktrace as core::fmt::Display>::fmt::h2e8cb764b7fe02e7
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/sys_common/backtrace.rs:58
   4:     0x55a16171bc4c - core::fmt::write::h7a1184eaee6a8644
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/core/src/fmt/mod.rs:1080
   5:     0x55a1616f2442 - std::io::Write::write_fmt::haeeb374d93a67eac
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/io/mod.rs:1516
   6:     0x55a1616fb11d - std::sys_common::backtrace::_print::h1d14a7f6ad632dc8
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/sys_common/backtrace.rs:61
   7:     0x55a1616fb11d - std::sys_common::backtrace::print::h301abac8bb2e3e81
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/sys_common/backtrace.rs:48
   8:     0x55a1616fb11d - std::panicking::default_hook::{{closure}}::hde0cb80358a6920a
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/panicking.rs:208
   9:     0x55a1616fadc8 - std::panicking::default_hook::h9b1a691049a0ec8f
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/panicking.rs:227
  10:     0x55a1616fb801 - std::panicking::rust_panic_with_hook::h2bdec87b60580584
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/panicking.rs:577
  11:     0x55a1616fb3a9 - std::panicking::begin_panic_handler::{{closure}}::h101ca09d9df5db47
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/panicking.rs:484
  12:     0x55a1616f90dc - std::sys_common::backtrace::__rust_end_short_backtrace::h3bb85654c20113ca
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/sys_common/backtrace.rs:153
  13:     0x55a1616fb369 - rust_begin_unwind
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/panicking.rs:483
  14:     0x55a161719871 - core::panicking::panic_fmt::h48c31e1e3d550146
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/core/src/panicking.rs:85
  15:     0x55a161719603 - core::option::expect_failed::hf3f43f1792267e24
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/core/src/option.rs:1226
  16:     0x55a1611b7897 - scaphandre::sensors::Topology::add_cpu_cores::h63e5518e58e301c8
  17:     0x55a16114d0bd - <scaphandre::sensors::powercap_rapl::PowercapRAPLSensor as scaphandre::sensors::Sensor>::generate_topology::h5bc10914f1385482
  18:     0x55a16114d4fa - <scaphandre::sensors::powercap_rapl::PowercapRAPLSensor as scaphandre::sensors::Sensor>::get_topology::h06a9dd8e7d085121
  19:     0x55a16119576e - <scaphandre::exporters::prometheus::PrometheusExporter as scaphandre::exporters::Exporter>::run::h6e2bd10bfd894fcb
  20:     0x55a161108a06 - scaphandre::run::ha4ed5db2b42f3873
  21:     0x55a1610f52f7 - scaphandre::main::hb3cd48c47ec910bd
  22:     0x55a1610f37d3 - std::sys_common::backtrace::__rust_begin_short_backtrace::h3c9a2d2e7724640c
  23:     0x55a1610f37e9 - std::rt::lang_start::{{closure}}::h829cbaf531010019
  24:     0x55a1616fbd17 - core::ops::function::impls::<impl core::ops::function::FnOnce<A> for &F>::call_once::he179d32a5d10d957
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/core/src/ops/function.rs:259
  25:     0x55a1616fbd17 - std::panicking::try::do_call::hcb3d5e7be089b2b4
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/panicking.rs:381
  26:     0x55a1616fbd17 - std::panicking::try::h7ac93b0cd56fb701
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/panicking.rs:345
  27:     0x55a1616fbd17 - std::panic::catch_unwind::h7b40e396c93a4fcd
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/panic.rs:382
  28:     0x55a1616fbd17 - std::rt::lang_start_internal::h142b9cc66267fea1
                               at /rustc/7eac88abb2e57e752f3302f02be5f3ce3d7adfb4/library/std/src/rt.rs:51
  29:     0x55a1610f54a2 - main
  30:     0x7f6f09c9dcb2 - __libc_start_main
  31:     0x55a1610f317a - _start
  32:                0x0 - <unknown>

```

# Thoughts
- Power Consumption is something interesting, it definitely has an impact.  That impact can also very in terms of how the power is created (IE: hydro-electric vs natural-gas --etc).
- Having the ability within Harvester to have that information at a glance on the Dashboard even listing out the VMs through KubeVirt could be neat, Scaphandre seemed pretty exciting, it's a shame that it simply won't work virtualized [here's an example of their Grafana Prometheus dashboard all rigged up](https://metrics.hubblo.org/d/GOHnbBO7z/scaphandre?orgId=1&refresh=15m)
- Having a 1:1 with Power Stats between bare-metal & virtualized would help lend to more automation because its something that's testable instead of testability hinging soley on bare-metal
- Even linking in a small db that contained info based on geographic region where the power usually comes from would of been neat as well
- There's the addded bonuses of just being able to track power consumption, spikes, anomolies and other interesting points a time series database would be useful to contain that information
- All in all, it woudl be great to get more detailed observability into power-consumption per VM on Harvester, based on some pending open-issues with Scaphandre that could yield itself to be possibly a good tool, maybe something to the affect of:
    - bare-metal Harvester:
        - we run Scaphandre in qemu mode 
        - new VMs that get spun up on KubeVirt we attach a running Scaphandre client in and run it to send to Rancher's Prometheus
    - virtualized Harvester:
        - we run on the KVM/Qemu host, Scaphandre in qemu mode
        - on the VM we could by chance run it also in qemu mode (possibly) and also in prometheus export mode, and any VMs created via nested virtualization, could be set up to send to Rancher's Prometheus too 