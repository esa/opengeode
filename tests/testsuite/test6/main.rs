#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod myfunction;
use myfunction::*;
use myfunction::dataview_uniqDef::*;

fn main() {
    unsafe {
        println!("[C Code] Running test");
        myfunction_startup();
        let mut test: asn1SccT_Int32 = 5;
        start_something(&mut test);
        myTimer();
    }
}
