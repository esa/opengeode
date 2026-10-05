#![allow(non_snake_case, non_upper_case_globals, unused_parens, unused_imports,
unused_variables, unused_mut, unused_assignments, dead_code)]
mod orchestrator;
use orchestrator::*;
use orchestrator::dataview_uniqDef::*;

fn main() {
    unsafe {
        orchestrator_startup();
        other();
        other();
    }
}
