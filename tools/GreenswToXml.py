import argparse
from calendar import c
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

    def toXmlCppcheckStyle(self, linePreamble):
        buffer = linePreamble + f"<error id=\"{self.code}\" severity=\"{self.severity}\" msg=\"{self.description}\" verbose=\"{self.verbose}\" file0=\"{self.file}\">\n"
        buffer = buffer + linePreamble + f"\t<location file=\"{self.file}\" line=\"{self.line}\"/>\n"
        buffer = buffer + linePreamble + "</error>\n"

        return buffer

def detectErrors(fileName):
    errors = []

    rowDelimeter = "+--------"
    tableState = TableState(1)
    reader = open(fileName, 'r')
    for line in reader:
        if rowDelimeter in line and tableState is TableState(1):
            tableState = TableState(2)
        
        if "code" in line and tableState is TableState(2):
            tableState = TableState(3)

        if rowDelimeter in line and tableState is TableState(3):
            tableState = TableState(4)

        if "|" in line and (tableState is TableState(4) or tableState is TableState(5)):
            tableState = TableState(5)
            errors.append(Error.create(line))

        if not "|" in line and not rowDelimeter in line and tableState is TableState(5):
            tableState = TableState(1)

    return errors

def generateXmlReportCppcheckStyle(inputFile, outputFile):
    errors = detectErrors(inputFile)

    writer = open(outputFile, 'w')
    writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    writer.write("<results version=\"1\">\n")
    writer.write("\t<GreenSW version=\"0.8\"/>\n")
    writer.write("\t<errors>\n")

    for error in errors:
        writer.write(error.toXmlCppcheckStyle("\t\t"))

    writer.write("\t</errors>\n")
    writer.write("</results>\n")

def generateXmlReportGtestStyle(inputFile, outputFile):
    errors = detectErrors(inputFile)

    errorsMap =  {}
    for error in errors:
        if not error.file in errorsMap: # key is not available
            errorsMap[error.file] = []
        
        errorsMap[error.file].append(error)

    writer = open(outputFile, 'w')
    writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")

    globalDetectsNumber = len(errors)
    writer.write(f"<testsuites tests=\"{globalDetectsNumber}\" failures=\"{globalDetectsNumber}\" disabled=\"0\" errors=\"0\" time=\"0\" timestamp=\"0\" name=\"AllSustainabilityErrors\">\n")
    
    for errorKey in errorsMap:
        defectFile = errorKey
        errorList = errorsMap[errorKey]
        defectsNumber = len(errorList)
        writer.write(f"\t<testsuite name=\"{defectFile}\" tests=\"{defectsNumber}\" failures=\"{defectsNumber}\" disabled=\"0\" skipped=\"0\" errors=\"0\" time=\"0\" timestamp=\"0\">\n")
    
        for error in errorList:
            testName = error.code
            className = error.file
            writer.write(f"\t\t<testcase name=\"{testName}\" status=\"run\" result=\"completed\" time=\"0\" timestamp=\"0\" classname=\"{className}\">\n")
    
            message = f"{error.file}:{error.line}\t{error.description}"
            writer.write(f"\t\t\t<failure message=\"{message}\" type\"\"></failure>\n")
    
            writer.write(f"\t\t</testcase>\n")
    
        writer.write(f"\t</testsuite>\n")
    
    writer.write(f"</testsuites>\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("fileName", help="Green SW file output to convert in junit xml file") 
    args = parser.parse_args(sys.argv[1:])

    print("fileName: {}".format(args.fileName))

    generateXmlReportGtestStyle(args.fileName, "greensw-results.xml")