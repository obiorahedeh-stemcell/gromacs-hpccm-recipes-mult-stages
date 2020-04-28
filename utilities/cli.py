'''
Author :
    * Muhammed Ahad <ahad3112@yahoo.com, maaahad@gmail.com>
'''
import sys
import os
import collections

import config


class CLI:
    def __init__(self, *, parser):
        self.parser = parser
        # Setting Command line arguments
        self.__set_cmd_options()
        # Parsing command line arguments
        self.args = self.parser.parse_args()

    def __set_cmd_options(self):
        # Minimal environment requirement
        self.parser.add_argument('--format', type=str, default='docker', choices=['docker', 'singularity'],
                                 help='Container specification format (default: docker).')
        self.parser.add_argument('--gromacs', type=str, default=config.DEFAULT_GROMACS_VERSION,
                                 help='set GROMACS version (default: {0}).'.format(config.DEFAULT_GROMACS_VERSION))

        self.parser.add_argument('--fftw', type=str,
                                 help='set fftw version. If not provided, GROMACS installtion will download and build FFTW from source.')

        self.parser.add_argument('--cmake', type=str, default=config.DEFAULT_CMAKE_VERSION,
                                 help='cmake version (default: {0}).'.format(config.DEFAULT_CMAKE_VERSION))

        self.parser.add_argument('--gcc', type=str, default=config.DEFAULT_GCC_VERSION,
                                 help='gcc version (default: {0}).'.format(config.DEFAULT_GCC_VERSION))

        # Optional environment requirement
        self.parser.add_argument('--cuda', type=str, help='enable and set cuda version.')

        self.parser.add_argument('--double', action='store_true', help='enable double precision.')
        self.parser.add_argument('--regtest', action='store_true', help='enable regression testing.')

        # set mutually exclusive options
        self.__set_mpi_options()
        self.__set_linux_distribution()

        # set gromacs engine specification
        self.__set_gromacs_engines()

    def __set_mpi_options(self):
        mpi_group = self.parser.add_mutually_exclusive_group()
        mpi_group.add_argument('--openmpi', type=str, help='enable and set OpenMPI version.')
        mpi_group.add_argument('--impi', type=str, help='enable and set Intel MPI version.')

    def __set_linux_distribution(self):
        linux_dist_group = self.parser.add_mutually_exclusive_group()
        linux_dist_group.add_argument('--ubuntu', type=str, help='enable and set linux dist : ubuntu.')
        linux_dist_group.add_argument('--centos', type=str, help='enable and set linux dist : centos.')

    def __set_gromacs_engines(self):
        self.parser.add_argument('--engines', type=str,
                                 metavar='simd={simd}:rdtscp={rdtscp}'.format(simd='|'.join(config.ENGINE_OPTIONS['simd']),
                                                                              rdtscp='|'.join(config.ENGINE_OPTIONS['rdtscp'])),
                                 nargs='+',
                                 default=[self.__get_default_gromacs_engine()],
                                 help='Specifying SIMD for multiple gmx engines within same image container (default: {default} ["based on your cpu"]).'.format(
                                     default=self.__get_default_gromacs_engine())
                                 )

    def __get_default_gromacs_engine(self):
        '''
        Decide the engine's Architecture by inspecting the underlying system where the script run
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
