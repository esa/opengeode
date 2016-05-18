#!/usr/bin/env python

import opengeode

# detect syntax errors (missing semi after "entry")

print('composite_state_body:')

test=opengeode.ogParser.parser_init(string=
'''state ENTRYA;
          substructure
            procedure entry EXTERNAL;
          endsubstructure ENTRYA;
''')

test.composite_state_body()

print('composite_state:')

test=opengeode.ogParser.parser_init(string=
'''state CHECKING;
        substructure
          state ENTRYA;
          substructure
            procedure entry EXTERNAL;
          endsubstructure ENTRYA;
        endsubstructure CHECKING;
''')

test.composite_state()

print('composite_state (should have no error)')

test=opengeode.ogParser.parser_init(string=
'''state CHECKING;
        substructure
          state ENTRYA;
          endstate ENTRYA;
        endsubstructure CHECKING;
''')

test.composite_state()
print('composite_state_body 2:')

test=opengeode.ogParser.parser_init(string=
'''state ENTRYA;
          endstate;
''')

test.composite_state_body()

print('from rm - reports that start must be before state:')
test=opengeode.ogParser.parser_init(string=
'''
STATE AGGREGATION DemoDeviceDACPStates;
        SUBSTRUCTURE
          STATE INTERNAL_MAPPINGS;
            SUBSTRUCTURE
              STATE STATELESS;
              ENDSTATE STATELESS;
              START;
              NEXTSTATE STATELESS;
            ENDSUBSTRUCTURE INTERNAL_MAPPINGS;
        ENDSUBSTRUCTURE DemoDeviceDACPStates;
''')

test.composite_state()

