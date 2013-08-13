# Import libraries
import time
import hmac
import sha
import base64
import urllib
import xml.dom.minidom as minidom

def getParameter(node, name, emptyStringIfEmpty=False, emptyStringIfAbsent=False):
    results = node.getElementsByTagName(name)
    if len(results) == 0:
        if emptyStringIfAbsent == True:
            return ""
    assert len(results) == 1, (node.toprettyxml(), name, len(results))
    childNodes = results[0].childNodes
    if emptyStringIfEmpty and len(childNodes) == 0:
        return ""
    else:
        assert len(childNodes) == 1, (node.toprettyxml(), name)
        return str(childNodes[0].data)

def getData(node):
    childNodes = node.childNodes
    assert len(childNodes) == 1, node
    return childNodes[0].data

class MturkError(Exception):
    def __init__(self, *args, **margs):
        Exception.__init__(self, *args, **margs)

#AWS_ACCESS_KEY_ID = 'AKIAJFI2KODE7KYFCIYA'
#AWS_SECRET_ACCESS_KEY = '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'

class Answer:
    def __init__(self, assignment, xml):
        self.assignment = assignment
        self.hit = assignment.hit
        self.questionIdentifier = getParameter(xml, "QuestionIdentifier")
        
        #each answer field from an ExternalQuestion is FreeText
        self.answer = getParameter(xml, "FreeText", emptyStringIfEmpty = True)

class Assignment:
    def __init__(self, hit, xml):
        self.hit = hit
        self.id = getParameter(xml, "AssignmentId")
        self.workerId = getParameter(xml, "WorkerId")
        self.hitId = getParameter(xml, "HITId")
        self.status = getParameter(xml, "AssignmentStatus")

        #kind of a hack to get around the fact that "QuestionFormAnswers" seems to be found before "Answer"
        answers = [getData(a) for a in xml.getElementsByTagName("Answer")]
        elements = minidom.parseString(answers[0]).getElementsByTagName("Answer")  #this gets the actual answers

        self.answers = [Answer(self, e) for e in elements]

        
class Hit:
    def __init__(self, xml):
        self.id = getParameter(xml, "HITId")
        self.typeId = getParameter(xml, "HITTypeId")
        self.title = getParameter(xml, "Title")
        self.description = getParameter(xml, "Description")
        self.keywords = getParameter(xml, "Keywords")
        self.status = getParameter(xml, "HITStatus")
        if 'RequesterAnnotation' in xml.toprettyxml():
            self.requesterAnnotation = getParameter(xml, "RequesterAnnotation")
        else:
            self.requesterAnnotation = None
        self.numAssignmentsCompleted = int(getParameter(xml, "NumberOfAssignmentsCompleted"))
        self.numAssignmentsAvailable = int(getParameter(xml, "NumberOfAssignmentsAvailable"))
        self.numAssignmentsPending = int(getParameter(xml, "NumberOfAssignmentsPending"))
        

        self.expiration = getParameter(xml, "Expiration")
        

class MturkServer:
    def __init__(self, access_key, secret_key, use_sandbox=False):
        self.access_key = access_key
        self.secret_key = secret_key
        #self.service_version = '2007-03-12'
        self.service_version = '2008-08-02'
        self.service_name = 'AWSMechanicalTurkRequester'
        if use_sandbox:
            self.url = 'https://mechanicalturk.sandbox.amazonaws.com/onca/xml?'
        else:
            self.url = 'https://mechanicalturk.amazonaws.com/onca/xml?'

        
    def generate_timestamp(self, gmtime):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

    def generate_signature(self, service, operation,
                           timestamp, secret_access_key):
        my_sha_hmac = hmac.new(secret_access_key,
                               service + operation + timestamp, sha)
        my_b64_hmac_digest = base64.encodestring(my_sha_hmac.digest()).strip()
        return my_b64_hmac_digest


    def makeOperation(self, operation):
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester',
                                            operation, timestamp,
                                            self.secret_key)
        return timestamp, signature


    def call(self, operation, **args):
        # Construct the request
        timestamp, signature = self.makeOperation(operation)
        parameters = {
            'Service': self.service_name,
            'Version': self.service_version,
            'AWSAccessKeyId': self.access_key,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            }
        parameters.update(args)

        #change this for sandbox or not sandbox
        
        result_xmlstr = urllib.urlopen(self.url, 
                                       urllib.urlencode(parameters)).read()
        result_xml = minidom.parseString(result_xmlstr)
        self.checkForErrors(result_xml)        
        return result_xml
    def checkForErrors(self, result):
        
        errorsNodes = result.getElementsByTagName('Errors')
        if errorsNodes:
            print 'There was an error processing your request:'
            for errorsNode in errorsNodes:
                for errorNode in errorsNode.getElementsByTagName('Error'):

                    errorCode = getParameter(errorNode, 'Code')
                    errorMessage = getParameter(errorNode, 'Message')

                    raise MturkError(errorCode + ": " + errorMessage)




    def getAccountBalance(self):
        result = self.call("GetAccountBalance")
        result = float(getParameter(result, 'Amount'))
        return result


    def getQualificationScore(self, qualificationTypeId, workerId):
        result = self.call("GetQualificationScore",
                           QualificationTypeId=qualificationTypeId,
                           SubjectId=workerId)
        value = getParameter(result, 'IntegerValue')
        return int(value)

    def unblockWorker(self, workerId):
        result = self.call("UnblockWorker",
                           WorkerId=workerId,
                           Operation="UnblockWorker")
        return result

    def getQualificationsForType(self, qualificationTypeId, pageNumber=1,
                                 pageSize=10):
        result = self.call("GetQualificationsForQualificationType",
                           QualificationTypeId=qualificationTypeId,
                           PageNumber=pageNumber,
                           PageSize=10)

        workerIds = [node.childNodes[0].data
                     for node in result.getElementsByTagName('SubjectId')]

        return workerIds

    def numQualificationsForType(self, qualificationTypeId):
        result = self.call("GetQualificationsForQualificationType",
                           QualificationTypeId=qualificationTypeId)

        numberOfResults = int(getParameter(result, "TotalNumResults"))
        return  numberOfResults
    
    def getWorkerAndQualificationScores(self, qualificationTypeId):

        numWorkers = self.numQualificationsForType(qualificationTypeId)

        workersRetrieved = 0
        page = 1

        while workersRetrieved < numWorkers:
            workerIds = self.getQualificationsForType(qualificationTypeId,
                                                      page)
            for workerId in workerIds:
                score = self.getQualificationScore(qualificationTypeId,
                                                   workerId)
                yield workerId, score
                workersRetrieved +=1 
            page += 1
        return
    def revokeQualification(self, qualificationTypeId, workerId, reason):
        self.call("RevokeQualification", SubjectId=workerId,
                  QualificationTypeId=qualificationTypeId,
                  Reason=reason)

    def revokeAll(self, qualificationTypeId, workerIds, reason):
        for workerId in workerIds:
            self.revokeQualification(qualificationTypeId, workerId, reason)

    def searchHits(self, sortProperty="Enumeration",
                   sortDirection="Ascending",
                   pageSize=100, pageNumber=1):
        return self.call("SearchHITs", SortProperty=sortProperty,
                         SortDirection=sortDirection,
                         PageSize=pageSize, PageNumber=pageNumber,
                         )

    def getAssignmentsForHit(self, hitId, assignmentStatus, 
                             pageSize=100, pageNumber=1):
                             

        return self.call("GetAssignmentsForHIT",
                         HITId=hitId, AssignmentStatus=assignmentStatus,
                         PageSize=pageSize, PageNumber=pageNumber,
                         )        

    def getAllAssignmentsForHit(self, hit, assignmentStatus="Approved"):
        totalAssignments = None
        page = 1

        assignments = []

        while totalAssignments == None or len(assignments) < totalAssignments:
            result = self.getAssignmentsForHit(hit.id, pageNumber=page,
                                               assignmentStatus=assignmentStatus)

            if totalAssignments == None:
                totalAssignments = int(getParameter(result, "TotalNumResults"))
            else:
                assert totalAssignments == int(getParameter(result,
                                                            "TotalNumResults"))

            for assignment in  result.getElementsByTagName('Assignment'):
                assignments.append(Assignment(hit, assignment))

            page += 1
        assert len(assignments) == totalAssignments, (len(assignments),
                                                      totalAssignments)
        return assignments

    def approveAssignment(self, assignmentId):

        return self.call("ApproveAssignment",
                         AssignmentId=assignmentId,
                         Operation="ApproveAssignment")

    def getAllHits(self):
        totalHits = None
        page = 1

        hits = []

        while totalHits == None or len(hits) < totalHits:
            result = self.searchHits(pageNumber=page)
            if totalHits == None:
                totalHits = int(getParameter(result, "TotalNumResults"))
            else:
                assert totalHits == int(getParameter(result, "TotalNumResults"))

            for hit in  result.getElementsByTagName('HIT'):
                hits.append(Hit(hit))

            page += 1
        assert len(hits) == totalHits, (len(hits), totalHits)
        return hits

def main():
    import sys
    access_key = sys.argv[1]
    secret_key = sys.argv[2]
    server = MturkServer(access_key, secret_key)

    qualificationTypeId = "1H5JU7DXY64VM6T6TJH9PL5R3G7ZAH"

    workerIds = []
    for workerId, score in server.getWorkerAndQualificationScores(qualificationTypeId):

        workerIds.append(workerId)
        
    print "got", len(workerIds), "workers"


if __name__ == "__main__":
    main()
