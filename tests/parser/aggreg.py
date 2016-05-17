#!/usr/bin/env python

import opengeode
y=opengeode.ogParser.parser_init(string='''state ENTRYA;
          substructure
            procedure entry EXTERNAL;
          endsubstructure ENTRYA;''')

y.composite_state_body()

z=opengeode.ogParser.parser_init(string='''state CHECKING;
        substructure
          state ENTRYA;
          substructure
            procedure entry EXTERNAL;
          endsubstructure ENTRYA;
        endsubstructure CHECKING;
''')

z.composite_state()
