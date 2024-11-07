/* TEMPLATE GENERATED TESTCASE FILE
Filename: CWE758_Undefined_Behavior__char_pointer_new_use_18.cpp
Label Definition File: CWE758_Undefined_Behavior.new.label.xml
Template File: point-flaw-18.tmpl.cpp
*/
/*
 * @description
 * CWE: 758 Undefined Behavior
 * Sinks: new_use
 *    GoodSink: Initialize then use data
 *    BadSink : Use data
 * Flow Variant: 18 Control flow: goto statements
 *
 * */

#include "std_testcase.h"

namespace CWE758_Undefined_Behavior__char_pointer_new_use_18
{

#ifndef OMITBAD

void bad()
{
    goto sink;
sink:
    {
        char * * pointer = new char *;
        char * data = *pointer; /* FLAW: the value pointed to by pointer is undefined */
        delete pointer;
        printLine(data);
    }
}

#endif /* OMITBAD */

#ifndef OMITGOOD

/* good1() reverses the blocks on the goto statement */
static void good1()
{
    goto sink;
sink:
    {
        char * data;
        data = "string";
        char * * pointer = new char *;
        *pointer = data; /* FIX: Assign a value to the thing pointed to by pointer */
        {
            char * data = *pointer;
            printLine(data);
        }
        delete pointer;
    }
}

void good()
{
    good1();
}

#endif /* OMITGOOD */

} /* close namespace */

/* Below is the main(). It is only used when building this testcase on
   its own for testing or for building a binary to use in testing binary
   analysis tools. It is not used when compiling all the testcases as one
   application, which is how source code analysis tools are tested. */

#ifdef INCLUDEMAIN

using namespace CWE758_Undefined_Behavior__char_pointer_new_use_18; /* so that we can use good and bad easily */

int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );
#ifndef OMITGOOD
    printLine("Calling good()...");
    good();
    printLine("Finished good()");
#endif /* OMITGOOD */
#ifndef OMITBAD
    printLine("Calling bad()...");
    bad();
    printLine("Finished bad()");
#endif /* OMITBAD */
    return 0;
}

#endif
