'''
Author :
    * Muhammed Ahad <ahad3112@yahoo.com, maaahad@gmail.com>
'''

from __future__ import print_function
import os
import sys
import collections
from distutils.version import StrictVersion

import hpccm

import config
from container.apps import Gromacs


# current module
current_module = sys.modules[__name__]

# common os packages required in the final image
os_packages = ['vim',
               'build-essential',
               'ca-certificates',
               'git',
               'gnupg',
               'libhwloc-dev',
               'libblas-dev',
               'liblapack-dev',
               'libx11-dev',
               'wget']


def get_base_image(*, args, cuda=None):
    '''
    Identify the base image to be used in every stage
    '''
    if cuda is not None:
        cuda_version_tag = 'nvidia/cuda:' + cuda + '-devel'
        if args.centos is not None:
            cuda_version_tag += '-centos' + args.centos
        elif args.ubuntu is not None:
            cuda_version_tag += '-ubuntu' + args.ubuntu
        else:
            raise RuntimeError('Logic error: no Linux distribution selected.')
        base_image = cuda_version_tag
    else:
        if args.ubuntu is not None:
            base_image = 'ubuntu:' + args.ubuntu
        elif args.centos is not None:
            base_image = 'centos:centos' + args.centos
        else:
            raise RuntimeError('No Linux distribution was chosen.')

    return base_image


def get_compiler(*, args, building_blocks):
    '''
    Identify the compiler. At this moment, only gnu compiler is supported
    '''
    if args.gcc is not None:
        building_blocks['compiler'] = hpccm.building_blocks.gnu(
            extra_repository=True,
            fortran=False,
            version=args.gcc
        )
    else:
        raise RuntimeError('Input Error: Only gcc compiler is supported')


def get_mpi(*, args, building_blocks):
    '''
    Identify mpi. At this moment only openmpi is supported
    '''
    if building_blocks.get('compiler', None) is not None:
        if hasattr(building_blocks['compiler'], 'toolchain'):
            cuda_enabled = True if args.cuda is not None else False
            if args.openmpi is not None:
                building_blocks['mpi'] = hpccm.building_blocks.openmpi(cuda=cuda_enabled,
                                                                       infiniband=False,
                                                                       toolchain=building_blocks['compiler'].toolchain,
                                                                       version=args.openmpi)
            elif args.impi is not None:
                # building_blocks['mpi'] = hpccm.building_blocks.intel_mpi(eula=True,
                #                                                          version=args.impi)

                raise RuntimeError('impi is not supported.')
        else:
            raise RuntimeError('compiler is not an HPCCM building block')
    else:
        raise RuntimeError('No compiler is available.')


def get_cmake(*, args, building_blocks):
    '''
    Cmake
    '''
    building_blocks['cmake'] = hpccm.building_blocks.cmake(eula=True, version=args.cmake)


def get_fftw(*, args, building_blocks, configure_opts=[], prefix='/usr/local/fftw'):
    '''
    fftw :
    '''
    if args.fftw is not None:
        if building_blocks.get('compiler', None) is not None:
            if hasattr(building_blocks['compiler'], 'toolchain'):
                configure_opts.extend(['--enable-shared', '--disable-static'])
                if not args.double:
                    configure_opts.append('--enable-float')

                building_blocks['fftw'] = hpccm.building_blocks.fftw(toolchain=building_blocks['compiler'].toolchain,
                                                                     configure_opts=configure_opts,
                                                                     prefix=prefix,
                                                                     version=args.fftw)
            else:
                raise RuntimeError('compiler is not an HPCCM building block')
        else:
            raise RuntimeError('No compiler is available.')


def get_dev_stage(*, stage_name='dev', args, building_blocks):
    '''
    This is the initial/development stage reponsible for building images with
    all required dependencies such as openmpi, fftw for GROMACS
    '''
    stage = hpccm.Stage()
    stage += hpccm.primitives.baseimage(image=get_base_image(args=args, cuda=args.cuda),
                                         _as=stage_name)

    for bb in ('compiler', 'mpi', 'cmake', 'fftw'):
        if building_blocks.get(bb, None) is not None:
            stage += building_blocks[bb]

    return stage


def get_deployment_stage(*, args, previous_stages, building_blocks, wrapper):
    '''
    This deploy the GROMACS along with it dependencies (fftw, mpi) to the final image
    '''
    stage = hpccm.Stage()
    stage += hpccm.primitives.baseimage(image=get_base_image(args=args, cuda=args.cuda))
    stage += hpccm.building_blocks.python(python3=True, python2=False, devel=False)
    stage += hpccm.building_blocks.packages(ospackages=os_packages)

    # adding runtime from compiler
    stage += building_blocks['compiler'].runtime()

    # adding runtime from previous stages/provided container
    # fftw
    if args.fftw_container:
        stage += hpccm.primitives.copy(_from=args.fftw_container,
                                       _mkdir=True,
                                       src=['/usr/local/lib'],
                                       dest='/usr/local/fftw/lib')

        stage += hpccm.primitives.copy(_from=args.fftw_container,
                                       _mkdir=True,
                                       src=['/usr/local/include'],
                                       dest='/usr/local/fftw/include')
        # adding fftw library path
        stage += hpccm.primitives.environment(
            variables={'LD_LIBRARY_PATH': '/usr/local/fftw/lib:$LD_LIBRARY_PATH'}
        )

    elif args.fftw:
        # library path will be added automatically by runtime
        stage += building_blocks['fftw'].runtime(_from='dev')


    # mpi
    if building_blocks.get('mpi', None) is not None:
        # This means, mpi has been installed in the dev stage
        stage += building_blocks['mpi'].runtime(_from='dev')


    if previous_stages.get('gromacs', None) is not None:
        stage += hpccm.primitives.copy(_from='gromacs',
                                       _mkdir=True,
                                       src=['/usr/local/gromacs'],
                                       dest='/usr/local/gromacs')
    # wrapper and gmx_chooser scripts
    scripts_directory = os.path.join(config.GMX_INSTALLATION_DIRECTORY, 'scripts')

    stage += hpccm.primitives.shell(commands=['mkdir -p {}'.format(scripts_directory)])

    # setting wrapper sctipt
    wrapper = os.path.join(scripts_directory, wrapper)
    stage += hpccm.primitives.copy(src='/scripts/wrapper.py', dest=wrapper)

    # copying the gmx_chooser script
    stage += hpccm.primitives.copy(src='/scripts/gmx_chooser.py',
                                   dest=os.path.join(scripts_directory, 'gmx_chooser.py'))
    # mod changing for the files in the directory scripts
    stage += hpccm.primitives.shell(commands=['chmod +x {}'.format(
        os.path.join(scripts_directory, '*')
    )])

    # # copying config file
    stage += hpccm.primitives.copy(src='config.py',
                                   dest=os.path.join(scripts_directory, 'config.py'))
    # setting environment variable so to make wrapper available to PATH
    stage += hpccm.primitives.environment(variables={'PATH': '{}:$PATH'.format(scripts_directory)})

    return stage


def prepare_and_cook_fftw(*, args):
    '''
    This routine will generate FFTW only container's specification file
    '''
    stage = hpccm.Stage()
    stage += hpccm.primitives.baseimage(image=get_base_image(args=args))
    building_blocks = collections.OrderedDict()

    get_compiler(args=args, building_blocks=building_blocks)
    get_fftw(args=args,
             building_blocks=building_blocks,
             configure_opts=['--enable-' + simd for simd in args.simd],
             prefix='/usr/local')

    for bb in building_blocks:
        stage += building_blocks[bb]

    print(stage)

def prepare_and_cook_gromacs(*, args):
    '''
    This routing will generate container's specificaton file for GROMACS
    '''
    stages = collections.OrderedDict()
    building_blocks = collections.OrderedDict()


    get_compiler(args=args, building_blocks=building_blocks)
    get_mpi(args=args, building_blocks=building_blocks)
    get_cmake(args=args, building_blocks=building_blocks)
    get_fftw(args=args,
             building_blocks=building_blocks,
             configure_opts=['--enable-sse2','--enable-avx',
                             '--enable-avx2', '--enable-avx512']
             )

    # create stages
    # development stage
    stages['dev'] = get_dev_stage(stage_name='dev', args=args, building_blocks=building_blocks)
    # Gromacs stage
    stages['gromacs'], wrapper = Gromacs(stage_name='gromacs',
                                         base_image=get_base_image(args=args, cuda=args.cuda),
                                         args=args,
                                         building_blocks=building_blocks)()

    # deployment stage
    stages['deploy'] = get_deployment_stage(args=args,
                                            previous_stages=stages,
                                            building_blocks=building_blocks,
                                            wrapper=wrapper)


    # cooking
    for stage in stages.values():
        if stage is not None:
            print(stage)
