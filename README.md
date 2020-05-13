# GROMACS
HPCCM recipes for GROMACS build and installation

#### Usage:

    $ ./gromacs_docker_builds.py -h/--help

    gromacs_docker_builds.py [-h] [--format {docker,singularity}]
                            [--gromacs {2020.1,2020.2}]
                            [--fftw {3.3.7,3.3.8}]
                            [--cmake {3.14.7,3.15.7,3.16.6,3.17.1}]
                            [--gcc {5,6,7,8,9}] [--cuda {9.1,10.0,10.1}]
                            [--double] [--regtest]
                            [--openmpi {3.0.0,4.0.0} | --impi {!!!Not Implemented Yet!!!}]
                            [--ubuntu {16.04,18.04,19.10,20.4} | --centos {5,6,7,8}]
                            [--engines simd=avx_512f|avx2|avx|sse2:rdtscp=on|off [simd=avx_512f|avx2|avx|sse2:rdtscp=on|off ...]]

##### Sample Commands To Generate Container Specification File
    ./gromacs_docker_builds.py --gromacs 2020.1 --ubuntu 18.04 --gcc 9 --cmake 3.17.1 --engines simd=sse2:rdtscp=off simd=sse2:rdtscp=on  --openmpi 3.0.0 --regtest --fftw 3.3.7> Dockerfile

## Running Image
The Available GROMACS wrapper binaries will be the followings based on `mpi` enabled or disabled (enabling double precision not tested yet):

* `gmx`
* `gmx_mpi`

#### With Singularity

#### Without Singularity

Bind the directory that you want Docker to get access to. Below is an example of running `mdrun` module using `gmx` wrapper:

    mkdir $HOME/data
    docker run -v $HOME/data:/data -w /data -it <image_name> gmx mdrun -s <.tpr file> -deffnm <ouput_file_name>


## Dependencies

* `python3`
* `libgomp1`
* `openmpi`
* `fftw`

