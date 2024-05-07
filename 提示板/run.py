import argparse
import sys

############################################################################
# Functions
############################################################################

def say(args):
    print args.msg

def yell(args):
    msg = args.msg
    if not args.no_upper:
        msg = msg.upper()
    print msg

############################################################################
# Parser support
############################################################################

class CmdParser(argparse.ArgumentParser):

    def __init__(self, function, name, description, args):
        super(CmdParser, self).__init__()
        self.function = function
        self.name = name
        self.description = description
        for arg_spec in args:
            if len(arg_spec) == 2:
                self.add_argument(arg_spec[0], **arg_spec[1])
            elif len(arg_spec) == 3:
                self.add_argument(arg_spec[0], arg_spec[1], **arg_spec[2])
            else:
                raise TypeError("invalid arg spec", arg)
        self.usage = self.format_command_usage(name)

    def format_command_usage(self, name):
        parts = self.format_usage().split(' ')
        return ' '.join([parts[1], name] + parts[2:])

    def __call__(self, argv):
        args = self.parse_args(argv)
        self.function(args)

class MainParser(argparse.ArgumentParser):

    def __init__(self, description, cmd_parsers):
        super(MainParser, self).__init__(description=description)
        self.add_argument('command', help='the command to run')
        self.epilog = 'Commands: %s' % self.format_commands(cmd_parsers)
        self.cmds = cmd_parsers

    def format_commands(self, cmd_parsers):
        return ' '.join([p.name for p in cmd_parsers])

    def __call__(self):
        args = self.parse_args(sys.argv[1:2])
        for cmd in self.cmds:
            if cmd.name == args.command:
                cmd(sys.argv[2:])
                break
        else:
            print("'%s' is not a valid command. See 'hello --help'"
                  % args.command)
            sys.exit(2)

############################################################################
# Parsers
############################################################################

say_parser = CmdParser(
    say, 'say', 'say hello or another message',
    [('-m', '--msg', {'help': 'the message to say',
                      'default': 'Hello World!'})])

yell_parser = CmdParser(
    yell, 'yell', 'yell hello or another message',
    [('-m', '--msg', {'help': 'the message to say',
                      'default': 'Hello World!'}),
     ('--no-upper', {'help': "don't capitalize the message",
                     'action': 'store_true'})])

main_parser = MainParser(
    'Script to perform various hello commands',
    [say_parser,
     yell_parser])

if __name__ == '__main__':
    main_parser()
