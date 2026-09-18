#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod operators;
use operators::*;
use operators::dataview_uniqDef::*;

fn main() {
    unsafe {
        operators_startup();
        run();
    }
}
