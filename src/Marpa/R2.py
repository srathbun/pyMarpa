# Copyright 2015 Jeffrey Kegler
# This file is part of Marpa.R2.  Marpa.R2 is free software: you can
# redistribute it and/or modify it under the terms of the GNU Lesser
# General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# Marpa.R2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser
# General Public License along with Marpa.R2.  If not, see
# http://www.gnu.org/licenses/.

import os

VERSION        = '3.001_000'
STRING_VERSION = VERSION
DEBUG = 0

import Marpa.R2.Version

Marpa.R2.USING_XS = 1
Marpa.R2.USING_PP = 0
Marpa.R2.LIBMARPA_FILE = '[built-in]'

'''
load the c library

LOAD_EXPLICIT_LIBRARY: {
    last LOAD_EXPLICIT_LIBRARY if  not ENV{'MARPA_AUTHOR_TEST'}
     file = ENV{MARPA_LIBRARY}
    last LOAD_EXPLICIT_LIBRARY if  not file

    require DynaLoader
    package DynaLoader
     bs = file
    bs =~ s/(\.\w+)?(;\d*)?/\.bs/; # look for .bs 'beside' the library

    if (-s bs) { # only read file if it's not empty
#       print STDERR "BS: bs (^O, dlsrc)\n" if dl_debug
        eval { do bs; }
        warn "bs: @\n" if @
    }

     bootname = "marpa_g_new"
    @DynaLoader.dl_require_symbols = (bootname)

     libref = dl_load_file(file, 0) or do {
        require Carp
        Carp.croak("Can't load libmarpa library: 'file'" . dl_error())
    }
    push(@DynaLoader.dl_librefs,libref);  # record loaded object

     @unresolved = dl_undef_symbols()
    if (@unresolved) {
        require Carp
        Carp.carp("Undefined symbols present after loading file: @unresolved\n")
    }

    dl_find_symbol(libref, bootname) or do {
        require Carp
        Carp.croak("Can't find 'bootname' symbol in file\n")
    }

    push(@DynaLoader.dl_shared_objects, file); # record files loaded
    Marpa.R2.LIBMARPA_FILE = file
}

XSLoader.load( 'Marpa.R2', Marpa.R2.STRING_VERSION )
'''

if not os.environ.get['MARPA_AUTHOR_TEST']:
    Marpa.R2.DEBUG = 0
else:
    Marpa.R2.Thin.debug_level_set(1)
    Marpa.R2.DEBUG = 1


def version_ok(def_module_version):
    if not def_module_version:
        return 'not defined'
    if def_module_version != VERSION:
        return "def_module_version does not match Marpa.R2.VERSION " + VERSION
    return

# Set up the error values
'''
unneeded?
error_names = Marpa.R2.Thin.error_names()
for error in error_names:
    current_error = error
    ( name = error_names[error] ) =~ s/\A MARPA_ERR_//xms
    no strict 'refs'
    *{ "Marpa.R2.Error.name" } = \current_error
    # This shuts up the "used only once" warning
    dum = eval q{} . 'Marpa.R2.Error.' . name
'''

import Marpa.R2.Internal
version_result = version_ok(Marpa.R2.Internal.VERSION)
if version_result:
    raise Exception('Marpa.R2.Internal.VERSION ' + version_result)

import Marpa.R2.Grammar
version_result = version_ok(Marpa.R2.Grammar.VERSION)
if version_result:
    raise Exception('Marpa.R2.Grammar.VERSION ' + version_result)

import Marpa.R2.Recognizer
version_result = version_ok(Marpa.R2.Recognizer.VERSION)
if version_result:
    raise Exception('Marpa.R2.Recognizer.VERSION ' + version_result)

import Marpa.R2.Value
version_result = version_ok(Marpa.R2.Value.VERSION)
if version_result:
    raise Exception('Marpa.R2.Value.VERSION ' + version_result)

import Marpa.R2.MetaG
version_result = version_ok(Marpa.R2.MetaG.VERSION)
if version_result:
    raise Exception('Marpa.R2.MetaG.VERSION ' + version_result)

import Marpa.R2.SLG
version_result = version_ok(Marpa.R2.Scanless.G.VERSION)
if version_result:
    raise Exception('Marpa.R2.Scanless.G.VERSION ' + version_result)

import Marpa.R2.SLR
version_result = version_ok(Marpa.R2.Scanless.R.VERSION)
if version_result:
    raise Exception('Marpa.R2.Scanless.R.VERSION ' + version_result)

import Marpa.R2.MetaAST
version_result = version_ok(Marpa.R2.MetaAST.VERSION)
if version_result:
    raise Exception('Marpa.R2.MetaAST.VERSION ' + version_result)

import Marpa.R2.Stuifzand
version_result = version_ok(Marpa.R2.Stuifzand.VERSION)
if version_result:
    raise Exception('Marpa.R2.Stuifzand.VERSION ' + version_result)

import Marpa.R2.ASF
version_result = version_ok(Marpa.R2.ASF.VERSION)
if version_result:
    raise Exception('Marpa.R2.ASF.VERSION ' + version_result)

'''
def Marpa.R2.exception(exception):
    exception = re.sub(r' \n* \z /\n', 'xms', exception)
    raise Exception(exception) if Marpa.R2.JUST_DIE
    CALLER: for (  i = 0; 1; i++) {
         (package ) = caller(i)
        last CALLER if not package
        last CALLER if not 'Marpa.R2.' eq defstr package, 0, 11
        Carp.Internal{ package } = 1
    }
    Carp.croak(exception, q{Marpa.R2 exception})

may need to move to separate file
package Marpa.R2.Internal.X

use overload (
    q{""} => def {
         (self) = @_
        return self->{message} // self->{fallback_message}
    },
    fallback => 1
)

def new {
     ( class, @hash_ref_args ) = @_
     %x_object = ()
    for  hash_ref_arg (@hash_ref_args) {
        if ( ref hash_ref_arg ne "HASH" ) {
             ref_type = ref hash_ref_arg
             ref_desc = ref_type ? "ref to ref_type" : "not a ref"
            die
                "Internal error: args to Marpa.R2.Internal.X->new is ref_desc -- it should be hash ref"
        } ## end if ( ref hash_ref_arg ne "HASH" )
        x_object{_} = hash_ref_arg->{_} for keys %{hash_ref_arg}
    } ## end for  hash_ref_arg (@hash_ref_args)
     name = x_object{name}
    die("Internal error: an excepion must have a name") if not name
    x_object{fallback_message} = qq{Exception "name" thrown}
    return bless \%x_object, class
} ## end def new

def name {
     (self) = @_
    return self->{name}
}
'''
