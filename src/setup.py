from distutils.core import setup

setup( 
        name = 'LabradExperimenter',
        version = '1.0',
        description = 'Scripting software for LabRAD framework',
        author = 'Christopher Reilly',
        author_email = 'reilly.christopher@gmail.com',
        url = 'https://github.com/creilly/LabRAD-Experimenter',
        packages = ['lrexp',
                    'lrexp.experimenter',
                    'lrexp.experimenter.dialogs',
                    'lrexp.functions',
                    'lrexp.functions.standard'],
        package_data = {'lrexp.experimenter':['icons/*.svg']}

     )
