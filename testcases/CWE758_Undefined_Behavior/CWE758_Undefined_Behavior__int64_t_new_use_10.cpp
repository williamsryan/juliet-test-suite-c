/* TEMPLATE GENERATED TESTCASE FILE
Filename: CWE758_Undefined_Behavior__int64_t_new_use_10.cpp
Label Definition File: CWE758_Undefined_Behavior.new.label.xml
Template File: point-flaw-10.tmpl.cpp
*/
/*
 * @description
 * CWE: 758 Undefined Behavior
 * Sinks: new_use
 *    GoodSink: Initialize then use data
 *    BadSink : Use data
 * Flow Variant: 10 Control flow: if(globalTrue) and if(globalFalse)
 *
 * */

#include "std_testcase.h"

namespace CWE758_Undefined_Behavior__int64_t_new_use_10
{

#ifndef OMITBAD

void bad()
{
    if(globalTrue)
    {
        {
            int64_t * pointer = new int64_t;
            int64_t data = *pointer; /* FLAW: the value pointed to by pointer is undefined */
            delete pointer;
            printLongLongLine(data);
        }
    }
}

#endif /* OMITBAD */

#ifndef OMITGOOD

/* good1() uses if(globalFalse) instead of if(globalTrue) */
static void good1()
{
    if(globalFalse)
    {
        /* INCIDENTAL: CWE 561 Dead Code, the code below will never run */
        printLine("Benign, fixed string");
    }
    else
    {
        {
            int64_t data;
            data = 5LL;
            int64_t * pointer = new int64_t;
            *pointer = data; /* FIX: Assign a value to the thing pointed to by pointer */
            {
                int64_t data = *pointer;
                printLongLongLine(data);
            }
            delete pointer;
        }
    }
}

/* good2() reverses the bodies in the if statement */
static void good2()
{
    if(globalTrue)
    {
        {
            int64_t data;
            data = 5LL;
            int64_t * pointer = new int64_t;
            *pointer = data; /* FIX: Assign a value to the thing pointed to by pointer */
            {
                int64_t data = *pointer;
                printLongLongLine(data);
            }
            delete pointer;
        }
    }
}

void good()
{
    good1();
    good2();
}

#endif /* OMITGOOD */

} /* close namespace */

/* Below is the main(). It is only used when building this testcase on
   its own for testing or for building a binary to use in testing binary
   analysis tools. It is not used when compiling all the testcases as one
   application, which is how source code analysis tools are tested. */

#ifdef INCLUDEMAIN

using namespace CWE758_Undefined_Behavior__int64_t_new_use_10; /* so that we can use good and bad easily */

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
