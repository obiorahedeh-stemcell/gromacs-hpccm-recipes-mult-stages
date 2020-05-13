# GROMACS
HPCCM recipes for GROMACS build and installation

#### Usage:

    $ ./gromacs_docker_builds.py -h/--help

##### Sample Commands
    ./gromacs_docker_builds.py --gromacs 2020.1 --ubuntu 18.04 --gcc 9 --cmake 3.17.1 --engines simd=sse2:rdtscp=off simd=sse2:rdtscp=on  --openmpi 3.0.0 --regtest --fftw 3.3.7> Dockerfile

## Running Image
The Available GROMACS wrapper binaries will be the followings based on `mpi` enabled or disabled (enabling double precision not tested yet):

* `gmx`
* `gmx_mpi`

#### Without Singularity

Bind the directory that you want Docker to get access to. Below is an example of running `mdrun` module using `gmx` wrapper:

    mkdir $HOME/data
    docker run -v $HOME/data:/data -w /data -it <image_name> gmx mdrun -s <.tpr file> -deffnm <ouput_file_name>


## Dependencies

* `python3`
* `libgomp1`
* `openmpi`
* `fftw`

