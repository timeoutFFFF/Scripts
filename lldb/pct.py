import lldb
from enum import IntEnum

# command script import scriptname

# Process and Thread States
class StateType(IntEnum):
    eStateInvalid   = 0
    eStateUnloaded  = 1 # Process is object is valid, but not currently loaded
    eStateConnected = 2 # Process is connected to remote debug services, but notlaunched or attached to anything yet
    eStateAttaching = 3 # Process is currently trying to attach
    eStateLaunching = 4 # Process is in the process of launching

    # The state changes eStateAttaching and eStateLaunching are both sent while
    # the private state thread is either not yet started or paused. For that
    # reason, they should only be signaled as public state changes, and not
    # private state changes.
    eStateStopped   = 5  #  Process or thread is stopped and can be examined.
    eStateRunning   = 6  # Process or thread is running and can't be examined.
    eStateStepping  = 7  # Process or thread is in the process of stepping and can  not be examined.
    eStateCrashed   = 8  #  Process or thread has crashed and can be examined.
    eStateDetached  = 9  # Process has been detached and can't be examined.
    eStateExited    = 10 # Process has exited and can't be examined.
    eStateSuspended = 11 # Process or thread is in a suspended state as far
                   # as the debugger is concerned while other processes
                   # threads get the chance to run.

class StopReason(IntEnum):
    eStopReasonInvalid       = 0
    eStopReasonNone          = 1
    eStopReasonTrace         = 2
    eStopReasonBreakpoint    = 3
    eStopReasonWatchpoint    = 4
    eStopReasonSignal        = 5
    eStopReasonException     = 6
    eStopReasonExec          = 7 #Program was re-exec'ed
    eStopReasonPlanComplete  = 8
    eStopReasonThreadExiting = 9
    eStopReasonInstrumentation = 10


def pct(debugger, command, result, internal_dict):
    '''
    The pct command executes the program until it reaches a call instruction or a return instruction.

    '''

    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()

    step_over = True

    state = process.GetState()

    # check if process has started yet or not
    if StateType.eStateInvalid == StateType(state):
        print(f"[-] Process has not started. Process state is eStateInvalid")
        return

    # Continue running till `call` or `ret` instruction reached
    while process.GetState() == StateType.eStateStopped:

        # Get the frame of the thread
        frame = thread.GetSelectedFrame()

        # check source code is available
        file = frame.GetLineEntry().GetFileSpec().GetFilename()


        if file:
            thread.StepOver()
        else:
            thread.StepInstruction(step_over)

        stream = lldb.SBStream()
        thread.GetStatus(stream)
        description = stream.GetData()

        print(description)


        # Get current address
        pc = frame.GetPCAddress()
        
               # Get SBInstruction
        pc_inst = target.ReadInstructions(pc, 1, "intel").GetInstructionAtIndex(0)

        if not pc.IsValid():
            print("Not Valid", pc)
            continue

        #print(f"{pc.GetLoadAddress(target):#x} => {pc_inst}")
        # Get Mnemonic of the instruction
        mnemonic = pc_inst.GetMnemonic(target)

        if "call" in mnemonic or "ret" in mnemonic:
            rdi = frame.FindRegister("rdi")
            char = rdi.GetType().GetBasicType(lldb.eBasicTypeChar).GetPointerType()
            chr_rdi = rdi.Cast(char)

            rsi = frame.FindRegister("rsi")
            chr_rsi = rsi.Cast(char)

            rdx = frame.FindRegister("rdx")
            chr_rdx = rdx.Cast(char)

            rcx = frame.FindRegister("rcx")
            chr_rcx = rcx.Cast(char)

            print(f"first arg : {rdi}, char : {chr_rdi}")
            print(f"Second arg: {rsi}, char : {chr_rsi}")
            print(f"third arg : {rdx}, char : {chr_rdx}")
            print(f"first arg : {rcx}, char : {chr_rcx}")
            #print(pc_inst.GetComment(target))
            break
            
            
            
# __lldb_init_module is a hook function that will be called each time your script module is loaded by the debugger.
# HandleCommand adds a new command with the name hello, implemented by the function helloWorld in the MyModule module.
def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f pct.pct pct -h "Executes the program until it reaches a call instruction or a return instruction."')
