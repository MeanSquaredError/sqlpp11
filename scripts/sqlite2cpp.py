#!/usr/bin/env python3

##
 # Copyright (c) 2013-2015, Roland Bock
 # Copyright (c) 2018, Egor Pugin
 # All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without modification,
 # are permitted provided that the following conditions are met:
 #
 #  * Redistributions of source code must retain the above copyright notice,
 #    this list of conditions and the following disclaimer.
 #  * Redistributions in binary form must reproduce the above copyright notice,
 #    this list of conditions and the following disclaimer in the documentation
 #    and/or other materials provided with the distribution.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 # ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 # WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 # IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 # INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 # BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 # DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 # LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 # OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 # OF THE POSSIBILITY OF SUCH DAMAGE.
 ##

import argparse
import os
import re
import sqlite3
import sys

INCLUDE = 'sqlpp11'
NAMESPACE = 'sqlpp'

# map sqlite3 types
types = {
    'integer': 'integer',
    'text': 'text',
    'blob': 'blob',
    'real': 'floating_point',
}

def main():
    parser = argparse.ArgumentParser(description='sqlpp11 cpp schema generator')
    parser.add_argument('ddl', help='path to ddl')
    parser.add_argument('target', help='path to target')
    parser.add_argument('namespace', help='namespace')
    parser.add_argument('-identity-naming',
                        help='Use table and column names from the ddl '
                        '(defaults to UpperCamelCase for tables and '
                        'lowerCamelCase for columns)',
                        action='store_true')
    args = parser.parse_args()

    pathToHeader = args.target + '.h'

    # execute schema scripts
    conn = sqlite3.connect(':memory:')
    conn.executescript(open(args.ddl).read())

    # set vars
    toClassName = identity_naming_func if args.identity_naming else class_name_naming_func
    toMemberName = identity_naming_func if args.identity_naming else member_name_naming_func
    DataTypeError = False

    header = open(pathToHeader, 'w')
    namespace = args.namespace
    nsList = namespace.split('::')

    # start printing
    print('#pragma once', file=header)
    print('', file=header)
    print('// generated by ' + ' '.join(sys.argv), file=header)
    print('', file=header)
    print('#include <' + INCLUDE + '/table.h>', file=header)
    print('#include <' + INCLUDE + '/data_types.h>', file=header)
    print('#include <' + INCLUDE + '/char_sequence.h>', file=header)
    print('', file=header)
    for ns in nsList:
        print('namespace ' + ns, file=header)
        print('{', file=header)

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables:
        table_name = table_name[0]

        if table_name.startswith('sqlite_'):
            continue

        sqlTableName = table_name
        tableClass = toClassName(sqlTableName)
        tableMember = toMemberName(sqlTableName)
        tableNamespace = tableClass + '_'
        tableTemplateParameters = tableClass
        print('  namespace ' + tableNamespace, file=header)
        print('  {', file=header)

        columns = cursor.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        for column in columns:
            sqlColumnName = column[1]
            columnClass = toClassName(sqlColumnName)
            tableTemplateParameters += ',\n               ' + tableNamespace + '::' + columnClass
            columnMember = toMemberName(sqlColumnName)
            sqlColumnType = column[2].lower()
            sqlCanBeNull = column[3] == 0 or column[3] == '0'
            print('    struct ' + columnClass, file=header)
            print('    {', file=header)
            print('      struct _alias_t', file=header)
            print('      {', file=header)
            print('        static constexpr const char _literal[] =  "' + escape_if_reserved(sqlColumnName) + '";', file=header)
            print('        using _name_t = sqlpp::make_char_sequence<sizeof(_literal), _literal>;', file=header)
            print('        template<typename T>', file=header)
            print('        struct _member_t', file=header)
            print('          {', file=header)
            print('            T ' + columnMember + ';', file=header)
            print('            T& operator()() { return ' + columnMember + '; }', file=header)
            print('            const T& operator()() const { return ' + columnMember + '; }', file=header)
            print('          };', file=header)
            print('      };', file=header)
            try:
                traitslist = [NAMESPACE + '::' + types[sqlColumnType]]
            except KeyError as e:
                print ('Error: datatype "'  + sqlColumnType + '"" is not supported.')
                DataTypeError = True
            requireInsert = True
            hasAutoValue = sqlColumnName == 'id'
            if hasAutoValue:
                traitslist.append(NAMESPACE + '::tag::must_not_insert')
                traitslist.append(NAMESPACE + '::tag::must_not_update')
                requireInsert = False
            if sqlCanBeNull:
                traitslist.append(NAMESPACE + '::tag::can_be_null')
                requireInsert = False
            if column[4]:
                requireInsert = False
            if requireInsert:
                traitslist.append(NAMESPACE + '::tag::require_insert')
            print('      using _traits = ' + NAMESPACE + '::make_traits<' + ', '.join(traitslist) + '>;', file=header)
            print('    };', file=header)

        print('  } // namespace ' + tableNamespace, file=header)
        print('', file=header)

        print('  struct ' + tableClass + ': ' + NAMESPACE + '::table_t<' + tableTemplateParameters + '>', file=header)
        print('  {', file=header)
        print('    struct _alias_t', file=header)
        print('    {', file=header)
        print('      static constexpr const char _literal[] =  "' + sqlTableName + '";', file=header)
        print('      using _name_t = sqlpp::make_char_sequence<sizeof(_literal), _literal>;', file=header)
        print('      template<typename T>', file=header)
        print('      struct _member_t', file=header)
        print('      {', file=header)
        print('        T ' + tableMember + ';', file=header)
        print('        T& operator()() { return ' + tableMember + '; }', file=header)
        print('        const T& operator()() const { return ' + tableMember + '; }', file=header)
        print('      };', file=header)
        print('    };', file=header)
        print('  };', file=header)


    for ns in reversed(nsList):
        print('} // namespace ' + ns, file=header)

    if (DataTypeError):
        print("Error: unsupported datatypes." )
        print("Possible solutions:")
        print("A) Implement this datatype (examples: sqlpp11/data_types)" )
        print("B) Extend/upgrade ddl2cpp (edit types map)" )
        print("C) Raise an issue on github" )
        sys.exit(10) #return non-zero error code, we might need it for automation

def get_include_guard_name(namespace, inputfile):
  val = re.sub("[^A-Za-z0-9]+", "_", namespace + '_' + os.path.basename(inputfile))
  return val.upper()

def identity_naming_func(s):
    return s

def repl_camel_case_func(m):
    if m.group(1) == '_':
        return m.group(2).upper()
    else:
        return m.group(1) + m.group(2).upper()

def class_name_naming_func(s):
    return re.sub("(^|\s|[_0-9])(\S)", repl_camel_case_func, s)

def member_name_naming_func(s):
    return re.sub("(\s|_|[0-9])(\S)", repl_camel_case_func, s)

def escape_if_reserved(name):
    reserved_names = [
        'GROUP',
        'ORDER',
    ]
    if name.upper() in reserved_names:
        return '!{}'.format(name)
    return name

if __name__ == '__main__':
    main()
    sys.exit(0)
