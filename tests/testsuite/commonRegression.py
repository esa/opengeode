import pexpect, sys

g_child = None

def test(binaries, expected, timeout):
    try:
        for binary in binaries:
            print ("Verifying", binary, " "*7,)
            global g_child
            g_child = pexpect.spawn(binary, timeout=timeout)
            total = len(expected)
            for cnt,elem in enumerate(expected):
                realList = [pexpect.TIMEOUT, pexpect.EOF]
                if isinstance(elem, list):
                    realList.extend(elem)
                else:
                    realList.append(elem)
                idx = g_child.expect_exact(realList)
                if 0 == idx:
                    print ("\nTimed out waiting for:", realList)
                    print (g_child)
                    return 1
                elif 1 == idx:
                    print ("\nUnexpected EOF waiting for:", realList)
                    print (g_child)
                    return 1
                else:
                    print("Received expected: ", elem)
                    sys.stdout.write("\b\b\b\b\b\b\b%3d/%3d" % (cnt+1,total))
                    sys.stdout.flush()
            print ("\nVerified ", binary, ": OK")
    except:
        print("Test failed...")
        return 1
    return 0
