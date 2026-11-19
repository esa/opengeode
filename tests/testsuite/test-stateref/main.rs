#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod complexsdl;
use complexsdl::*;
// asn1scc emits one file pair per ASN.1 module, so the type lives in the
// module that declares it (TESTBENCH2-DATAVIEW), not in the first
// module's legacy 'dataview_uniqDef' alias.
use complexsdl::testbench2_dataviewDef::*;

fn main() {
    unsafe {
        let mut x: asn1SccMyInteger = 0;
        complexsdl_startup();
        impulse(&mut x);
        impulse(&mut x);
    }
}
