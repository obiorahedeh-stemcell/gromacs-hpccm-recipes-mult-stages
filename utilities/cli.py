'''
Author :
    * Muhammed Ahad <ahad3112@yahoo.com, maaahad@gmail.com>
'''
import sys
import os
import collections

import config


class CLI:
    '''
    Command Line Interface to gather information regarding the container specification from the user
    User can choose to have multiple GROMACS build within the same container image
    '''

    def __init__(self, *, parser):
        self.parser = parser
        # Setting Command line arguments
        self.__set_cmd_options()
        # Parsing command line arguments
        self.args = self.parser.parse_args()

    def __set_cmd_options(self):
        '''
        Seting up command line options with all available choices for each option
        '''
        self.parser.add_argument('--format', type=str, default='docker', choices=['docker', 'singularity'],
                                 help='CONTAINER specification format (DEFAULT: docker).')
        self.parser.add_argument('--gromacs', type=str, default=config.DEFAULT_GROMACS_VERSION,
                                 choices=['2019.2', '2020.1', '2020.2'],
                                 help='GROMACS version (DEFAULT: {0}).'.format(config.DEFAULT_GROMACS_VERSION))

        # TODO: add option to accept fftw container as input
        fftw_group = self.parser.add_mutually_exclusive_group()
        fftw_group.add_argument('--fftw', type=str, choices=['3.3.7', '3.3.8'],
                                 help=('FFTW version. '
                                       'GROMACS installation will download and '
                                       'build FFTW from source if neither of '
                                       '--fftw or --fftw-container argument provided'))
        fftw_group.add_argument('--fftw-container', type=str,
                                help=('FFTW container to be used instead of '
                                      'building it from sources. '
                                      'GROMACS installation will download and '
                                      'build FFTW from source if neither of '
                                      '--fftw or --fftw-container argument provided'))
        self.parser.add_argument('--fftw-gen-recipe', action="store_true",
                                 help='Enable this will generate recipe for FFTW only container. [Not Implemented Yet]')


        self.parser.add_argument('--cmake', type=str, default=config.DEFAULT_CMAKE_VERSION,
                                 choices=['3.14.7', '3.15.7', '3.16.6', '3.17.1'],
                                 help='CMAKE version (DEFAULT: {0}).'.format(config.DEFAULT_CMAKE_VERSION))

        self.parser.add_argument('--gcc', type=str, default=config.DEFAULT_GCC_VERSION,
                                 choices=['5', '6', '7', '8', '9'],
                                 help='GCC version (DEFAULT: {0}).'.format(config.DEFAULT_GCC_VERSION))

        self.parser.add_argument('--cuda', type=str,
                                 choices=['9.1', '10.0', '10.1'],
                                 help='ENABLE and set CUDA version.')

        self.parser.add_argument('--double', action='store_true', help='ENABLE DOUBLE precision (!!!NOT TESTED YET!!!).')
        self.parser.add_argument('--regtest', action='store_true', help='ENABLE REGRESSION testing.')

        # set mutually exclusive options
        self.__set_mpi_options()
        self.__set_linux_distribution()

        # set gromacs engine specification
        self.__set_gromacs_engines()

    def __set_mpi_options(self):
        '''
        Setting up mpi option. User can choose only one option from (openmpi, impi, ....)
        At this moment, only openmpi is supported
        '''
        mpi_group = self.parser.add_mutually_exclusive_group()
        mpi_group.add_argument('--openmpi', type=str,
                               choices=['3.0.0', '4.0.0'],
                               help='ENABLE and set OpenMPI version.')
        mpi_group.add_argument('--impi', type=str,
                               choices=['2018.3-051', '2019.6-088'],
                               help='ENABLE and set IntelMPI version. [ Not Implemented Yet!!! ]')

    def __set_linux_distribution(self):
        '''
        User can specify linux distro that will be the base image of the final container image
        Available choices: {ubuntu, centos}
        '''
        linux_dist_group = self.parser.add_mutually_exclusive_group()
        linux_dist_group.add_argument('--ubuntu', type=str,
                                      choices=['16.04', '18.04', '19.10', '20.4'],
                                      help='ENABLE and set UBUNTU version as BASE IMAGE.')
        linux_dist_group.add_argument('--centos', type=str,
                                      choices=['5', '6', '7', '8'],
                                      help='ENABLE and set CENTOS version as BASE IMAGE.')

    def __set_gromacs_engines(self):
        '''
        Using this option user can specify SIMD instruction set from [sse2, avx, avx, avx_512f].
        For each SIMD instruction set, user can also specify whether to turn on RDTSCP ON or OFF
        '''
        self.parser.add_argument('--engines', type=str,
                                 metavar='simd={simd}:rdtscp={rdtscp}'.format(simd='|'.join(config.ENGINE_OPTIONS['simd']),
                                                                              rdtscp='|'.join(config.ENGINE_OPTIONS['rdtscp'])),
                                 nargs='+',
                                 default=[self.__get_default_gromacs_engine()],
                                 help='SIMD for multiple GROMACS engines within same image container. List of Available choices: {choices} \n(DEFAULT: {default} ["Based on scripts HOST"]).'.format(
                                     choices=['simd=sse2:rdtscp=off', 'simd=sse2:rdtscp=on', 'simd=avx:rdtscp=off', 'simd=avx:rdtscp=on',
                                              'simd=avx2:rdtscp=off', 'simd=avx2:rdtscp=on', 'simd=avx_512f:rdtscp=off', 'simd=avx_512f:rdtscp=on'],
                                     default=self.__get_default_gromacs_engine())
                                 )

    def __get_default_gromacs_engine(self):
        '''
        Decide the engine's SIMD Architecture by inspecting the underlying system where the script runs
        '''
        if sys.platform in ['linux', 'linux2']:
            flags = os.popen('cat /proc/cpuinfo | grep ^flags | head -1').read()
        elif sys.platform in ['darwin', ]:
            flags = os.popen('sysctl -n machdep.cpu.features machdep.cpu.leaf7_features').read()
        else:
            raise SystemExit('Windows not supported yet...')

        engine = 'simd={simd}:rdtscp={rdtscp}'
        for simd in config.ENGINE_OPTIONS['simd']:
            if simd.lower() in flags.lower():
                break

        # loop variable simd is not localized, so we can use it here
        engine = engine.format(simd=simd,
                               rdtscp='on' if 'rdtscp' in flags.lower() else 'off')

        return engine
