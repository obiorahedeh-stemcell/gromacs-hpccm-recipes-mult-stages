# GROMACS
HPCCM recipes for generating FFTW/GROMACS contianer specification file.

#### The recipe contains two sub-commands, one for FFTW and the other for GROMACS :

    $ ./generate_specifications_file.py -h
    ./generate_specifications_file.py [-h] {fftw,gmx} ...

## Generating Container Specification File for FFTW

    $ ./generate_specifications_file.py fftw -h/--help
    ./generate_specifications_file.py fftw [-h] [--format {docker,singularity}] [--gcc {5,6,7,8,9}] [--double]
                                              (--ubuntu {16.04,18.04,19.10,20.4} | --centos {5,6,7,8}) [--fftw {3.3.7,3.3.8}] --simd
                                              {sse2,avx,avx2,avx512} [{sse2,avx,avx2,avx512} ...]

##### Sample command to Generate Container Specification File for Docker :

    ./generate_specifications_file.py fftw --format docker --ubuntu 18.04  --fftw 3.3.7 --gcc 8 --simd avx avx2 sse2 avx512 > Dockerfile

## Generating Container Specification File for GROMACS

Note that the options listed here for `gcc`, `ubuntu`, `centos`, `gromacs`, `fftw`, `cuda`, `cmake`, `openmpi`, `impi` are guides to what can be used, and these options are not set to specific choices. `engine` and `simd` choices are constrained though, and the source code will need to be modified if you which to extend these.

    $ ./generate_specifications_file.py gmx -h/--help

    ./generate_specifications_file.py gmx [-h] [--format {docker,singularity}] [--gcc {5,6,7,8,9}] [--double]
                                           (--ubuntu {16.04,18.04,19.10,20.4} | --centos {5,6,7,8}) [--gromacs {2019.2,2020.1,2020.2,2020.3}]
                                           [--fftw {3.3.7,3.3.8} | --fftw-container FFTW_CONTAINER] [--cuda {9.1,10.0,10.1}] [--regtest]
                                           [--cmake {3.14.7,3.15.7,3.16.6,3.17.1}] [--openmpi {3.0.0,4.0.0} | --impi {2018.3-051,2019.6-088}]
                                           [--engines simd=avx_512f|avx2|avx|sse2:rdtscp=on|off [simd=avx_512f|avx2|avx|sse2:rdtscp=on|off ...]]

##### Sample command to Generate Container Specification File for Docker provided with `fftw version` :
    ./generate_specifications_file.py gmx --format docker --gromacs 2020.1 --ubuntu 18.04 --gcc 9 --cmake 3.17.1 --engines simd=sse2:rdtscp=off simd=sse2:rdtscp=on  --openmpi 3.0.0 --regtest --fftw-container gromacs/fftw > Dockerfile

##### Sample command to Generate Container Specification File for Docker provided with `fftw container` :
    ./generate_specifications_file.py gmx --format docker --gromacs 2020.1 --ubuntu 18.04 --gcc 9 --cmake 3.17.1 --engines simd=sse2:rdtscp=off simd=sse2:rdtscp=on  --openmpi 3.0.0 --regtest --fftw 3.3.7> Dockerfile

##### Choosing `SIMD` and `RDTSCP` instruction for `GROMACS` build using the option `--engines` :
###### Value format:
     simd=avx_512f|avx2|avx|sse2:rdtscp=on|off
###### Example (Warning: There should be no space in `--engines` option value)
     simd=avx2:rdtscp=on

It is possible to choose multiple value for `--engines` to have multiple `GROMACS` installation within the same container as follows:

    --engines simd=sse2:rdtscp=on simd=avx2:rdtscp=on

## Generating Docker Image
    docker build -t <image_name> .

The above commands assumes that it is run from the directory `gromacs-hpccm-recipes-mult-stages` and the `Dockerfile` lives in this directory.
The reason is that, directory `gromacs-hpccm-recipes-mult-stages` contains some utility scripts what will be
copied to the final image. In the essence, one have to use this directory as build context.

## Running Image
The Available GROMACS wrapper binaries will be the followings based on `mpi` enabled or disabled (enabling double precision not tested yet):

* `gmx`
* `gmx_mpi`

#### With Singularity
Build Singularity image from Docker:

    singularity build <name of image to be built> docker://<docker_image>

Example of running `mdrun` with `gmx_mpi` wrapper:

    mpirun -np <no of processes> singularity exec -B <host directory to bind> <singularity image> gmx_mpi mdrun -s <.tpr file> -deffnm <ouput_file_name>

To enable NVIDIA GPU support, please add `--nv` flag to `singularity exec` command as follows:

    mpirun -np <no of processes> singularity exec --nv -B <host directory to bind> <singularity image> gmx_mpi mdrun -s <.tpr file> -deffnm <ouput_file_name>

Before running the above command, you have to make sure that you have added appropriate module for `gcc`, `openmpi` and `cuda`.

#### Without Singularity

Bind the directory that you want Docker to get access to. Below is an example of running `mdrun` module using `gmx` wrapper:

    mkdir $HOME/data
    docker run -v $HOME/data:/data -w /data -it <image_name> gmx mdrun -s <.tpr file> -deffnm <ouput_file_name>


## Dependencies

* `python3`
* `libgomp1`
* `openmpi`
* `fftw`


