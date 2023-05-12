import argparse
import enum
import sys
 
class TableState(enum.Enum):
    Empty = 1
    PreHeader = 2
    Header = 3
    PostHeader = 4
    Content = 5

class Error:
    def __init__(self):
        self.code = ""
        self.file = ""
        self.line = ""
        self.description = ""
        self.verbose = ""
        self.severity = "sustainability"
            
    @staticmethod
    def create(line):
        error = Error()
        components = line.split('|')
        if len(components) > 4:
            error.code = components[1]
            error.file = components[2].strip()
            error.line = components[3].strip()
            error.description = components[4].strip()
        
        return error

    def toXml(self, linePreamble):
        buffer = linePreamble + f"<error id=\"{self.code}\" severity=\"{self.severity}\" msg=\"{self.description}\" verbose=\"{self.verbose}\" file0=\"{self.file}\">\n"
        buffer = buffer + linePreamble + f"\t<location file=\"{self.file}\" line=\"{self.line}\"/>\n"
        buffer = buffer + linePreamble + "</error>\n"

        return buffer

def detectErrors(fileName):
    errors = []

    tableState = TableState(1)
    isHeader = False
    isElement = True
    reader = open(fileName, 'r')
    for line in reader:
        if "+---------+-------------------------+------+---------------------------+" in line and tableState is TableState(1):
            tableState = TableState(2)
        
        if "code" in line and tableState is TableState(2):
            tableState = TableState(3)

        if "+---------+-------------------------+------+---------------------------+" in line and tableState is TableState(3):
            tableState = TableState(4)

        if "|" in line and (tableState is TableState(4) or tableState is TableState(5)):
            tableState = TableState(5)
            errors.append(Error.create(line))

        if not "|" in line and not "+---------+-------------------------+------+---------------------------+" in line and tableState is TableState(5):
            tableState = TableState(1)

    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("fileName", help="Green SW file output to convert in junit xml file") 
    args = parser.parse_args(sys.argv[1:])

    print("fileName: {}".format(args.fileName))

    errors = detectErrors(args.fileName)

    writer = open("greensw-results.xml", 'w')
    writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    writer.write("<results version=\"1\">\n")
    writer.write("\t<GreenSW version=\"0.8\"/>\n")
    writer.write("\t<errors>\n")

    for error in errors:
        writer.write(error.toXml("\t\t"))

    writer.write("\t</errors>\n")
    writer.write("</results>\n")