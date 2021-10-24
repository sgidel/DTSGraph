# DTSGraph
A simple tool for creating dependency graphs from a device tree file

This tool was created in an effort to make it easier to understand very complicated device tree structures.

The default output is a graphviz svg. If `pygraphviz` is not installed, it will default to formatted JSON output.

## Usage:
```
dtsgraph.py [-h] [-f {json,graphimg,dot}] [-o FILENAME] [-n] srcdir dts

Generate a graph of device tree dependencies

positional arguments:
  srcdir                Source directory to look in
  dts                   Top level device tree to parse, relative to srcdir

optional arguments:
  -h, --help            show this help message and exit
  -f {json,graphimg,dot}, --format {json,graphimg,dot}
                        Graph output type, defaults to graphimg
  -o FILENAME, --outputfile FILENAME
                        Use custom output file name, defaults to dts name. In JSON mode, 'stdout' will print directly to console
  -n, --noheader        Disable resolution of .h files
```

## Sample Output:
Using Nvidia Jetson nano device tree w/ JSON output mode
```
$ ./dtsgraph.py ../jetson_cam/kbuild/hardware/ nvidia/platform/t210/porg/kernel-dts/tegra210-p3448-0000-p3449-0000-b00.dts -f json -o stdout
{
    "nvidia/platform/t210/porg/kernel-dts/tegra210-p3448-0000-p3449-0000-b00.dts": {
        "nvidia/platform/t210/porg/kernel-dts/tegra210-porg-p3448-common.dtsi": {
            "nvidia/platform/t210/common/kernel-dts/t210-common-platforms/tegra210-common.dtsi": {
                "nvidia/soc/t210/kernel-dts/tegra210-soc/tegra210-soc-shield.dtsi": {
                    "nvidia/soc/t210/kernel-dts/tegra210-soc/tegra210-soc-base.dtsi": {
                        "nvidia/soc/tegra/kernel-include/dt-bindings/version.h": {},
                        "nvidia/soc/tegra/kernel-include/dt-bindings/interrupt-controller/arm-gic.h": {
                            "nvidia/soc/tegra/kernel-include/dt-bindings/interrupt-controller/irq.h": {}
                        },
                        "nvidia/soc/tegra/kernel-include/dt-bindings/clock/tegra210-car.h": {},
                        "nvidia/soc/tegra/kernel-include/dt-bindings/reset/tegra210-car.h": {},
                        "nvidia/soc/tegra/kernel-include/dt-bindings/memory/tegra-swgroup.h": {},
                        "nvidia/soc/t210/kernel-dts/tegra210-soc/tegra210-thermal.dtsi": {
                            "nvidia/soc/tegra/kernel-include/dt-bindings/thermal/tegra124-soctherm.h": {},
                            "nvidia/soc/tegra/kernel-include/dt-bindings/thermal/thermal.h": {}
                        },
...
```