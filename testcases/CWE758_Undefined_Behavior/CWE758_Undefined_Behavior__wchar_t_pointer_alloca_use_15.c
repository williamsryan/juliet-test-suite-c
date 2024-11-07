/* TEMPLATE GENERATED TESTCASE FILE
Filename: CWE758_Undefined_Behavior__wchar_t_pointer_alloca_use_15.c
Label Definition File: CWE758_Undefined_Behavior.alloc.label.xml
Template File: point-flaw-15.tmpl.c
*/
/*
 * @description
 * CWE: 758 Undefined Behavior
 * Sinks: alloca_use
 *    GoodSink: Initialize then use data
 *    BadSink : Use data from alloca without initialization
 * Flow Variant: 15 Control flow: switch(6)
 *
 * */

#include "std_testcase.h"

#ifndef OMITBAD

void CWE758_Undefined_Behavior__wchar_t_pointer_alloca_use_15_bad()
{
    switch(6)
    {
    case 6:
    {
        wchar_t * * pointer = (wchar_t * *)ALLOCA(sizeof(wchar_t *));
        wchar_t * data = *pointer; /* FLAW: the value pointed to by pointer is undefined */
        printWLine(data);
    }
    break;
    default:
        /* INCIDENTAL: CWE 561 Dead Code, the code below will never run */
        printLine("Benign, fixed string");
        break;
    }
}

#endif /* OMITBAD */

#ifndef OMITGOOD

/* good1() changes the switch to switch(5) */
static void good1()
{
    switch(5)
    {
    case 6:
        /* INCIDENTAL: CWE 561 Dead Code, the code below will never run */
        printLine("Benign, fixed string");
        break;
    default:
    {
        wchar_t * data;
        wchar_t * * pointer = (wchar_t * *)ALLOCA(sizeof(wchar_t *));
        data = L"string";
        *pointer = data; /* FIX: Assign a value to the thing pointed to by pointer */
        {
            wchar_t * data = *pointer;
            printWLine(data);
        }
    }
    break;
    }
}

/* good2() reverses the blocks in the switch */
static void good2()
{
    switch(6)
    {
    case 6:
    {
        wchar_t * data;
        wchar_t * * pointer = (wchar_t * *)ALLOCA(sizeof(wchar_t *));
        data = L"string";
        *pointer = data; /* FIX: Assign a value to the thing pointed to by pointer */
        {
            wchar_t * data = *pointer;
            printWLine(data);
        }
    }
    break;
    default:
        /* INCIDENTAL: CWE 561 Dead Code, the code below will never run */
        printLine("Benign, fixed string");
        break;
    }
}

void CWE758_Undefined_Behavior__wchar_t_pointer_alloca_use_15_good()
{
    good1();
    good2();
}

#endif /* OMITGOOD */

/* Below is the main(). It is only used when building this testcase on
   its own for testing or for building a binary to use in testing binary
   analysis tools. It is not used when compiling all the testcases as one
   application, which is how source code analysis tools are tested. */

#ifdef INCLUDEMAIN

int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );
#ifndef OMITGOOD
    printLine("Calling good()...");
    CWE758_Undefined_Behavior__wchar_t_pointer_alloca_use_15_good();
    printLine("Finished good()");
#endif /* OMITGOOD */
#ifndef OMITBAD
    printLine("Calling bad()...");
    CWE758_Undefined_Behavior__wchar_t_pointer_alloca_use_15_bad();
    printLine("Finished bad()");
#endif /* OMITBAD */
    return 0;
}

#endif
