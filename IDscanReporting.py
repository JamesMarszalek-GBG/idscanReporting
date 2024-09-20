'''
TASKS:
1) Dictionary List of Customers.
1.1) Check if customer name DIR is made. Check if customer name AND month DIR made.
2) Iterate through list.
3) Get Token and Security Headers
4) Get CSV File
5) Call and Thread first API
6) Call and Thread second API
7) Collate results.

"Search/GetEvaluatedPersonEntryValidationResults?id="
"journey/get?journeyID="


'''
class Loader():
    loaderTotal = 0
    currentLoaderCount = 0

import random
import os
import datetime
import requests
import csv
import threading
import shutil
import traceback


########## SETUP ##########
directory_name = "Reports"
root_directory = os.getcwd()
directory_path = os.path.join(root_directory, directory_name)
if not os.path.exists(directory_path):
    os.mkdir(directory_path)
    print(f"Directory '{directory_name}' created in {root_directory}")
else:
    print(f"Directory '{directory_name}' already exists in {root_directory}")
########## SETUP ##########


vizHeader = ["JourneyID", "High Level Result", "Overriden Result", "Facematch Score", "Triple Scan Attempts", "Browser",
          "Platform", "Country", "Document Type", "Scan Date Time", "Dropout Stage", "Total Journey Time",
          "Liveness Time", "Auto Capture Time", "Auto Capture Used", "Manual Capture Used", "File Upload Used",
          "Blue Issue", "Glare Issue", "Low Resolution Issue", "Full Document Not In View Issue", "Age Range", "Journey Definition Name", "UserName", "Front Side Result", "Back Side Result", "POA Result", "NFC Result", "Liveness Result", "Selfie Result", "Data Result", "Device Manufacturer", "Device Model", "Device Version", "Device Connectivity Method", "NFC Cross Ref Result", "NFC State", "Liveness Score", "Liveness Fail Reason", "Expiry Date", "Document Name", "First Name", "Middle Name", "Last Name", "Auth Flags Triggered", "MJCS Version Number", "MJCS App ID"]




reportingClients = [
{
        "name": "Name",
        "username": "idscanUsername",
        "password": "idscanPW",
        "days": 10,
        "url": "https://prod.idscan.cloud/idscanenterprisesvc",
        "imageAnalysis": "n",
        "threads": 10,
        "override": False,
        "overrideName": "May.csv",
        "dedupe": False
    }
]

def dedupe():
    result_order = ["Passed", "Refer", "Expired", "NotAccepted", "Notsupported", "Undefined"]

    def get_rank(outcome):
        return result_order.index(outcome) if outcome in result_order else len(result_order)

    with open(csv_file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)

    best_rows = {}

    for row in data:
        key = (row['Full Name'], row['Birth Date'])
        current_rank = get_rank(row['Journey Outcome'])

        if key not in best_rows or current_rank < get_rank(best_rows[key]['Journey Outcome']):
            best_rows[key] = row

    with open(csv_file_name, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in best_rows.values():
            writer.writerow(row)

    print(f"Deduplicated data has been written to {csv_file_name}")


def dupeByDocNo(fileName, filesaveLocation):
    saveLocation = filesaveLocation+"/Duplicates.txt"
    totalCount = 0
    nameList = []
    with open(fileName, errors="ignore") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if (len(row[9]) > 3) and (len(row[12]) > 3):
                nameList.append([row[9], row[12], row[0], row[18],
                                 row[8], row[10]])  # Full Name (not in use), DocNumber, GUID, Result, TimeCreated, DoB.
        nameList.pop(0)
        # print(nameList)

    docNumberDuplicatesFile = open(saveLocation, "w")

    for i in range(len(nameList)):
        for j in range(len(nameList)):
            if nameList[i][2] != nameList[j][2]:  # GUIDs Don't Match
                if nameList[i][1] == nameList[j][1]:  # Doc Numbers also match
                    from datetime import datetime
                    # Convert string to datetime object
                    time1_obj = datetime.strptime(nameList[i][4], "%Y-%m-%dT%H:%M:%SZ")
                    time2_obj = datetime.strptime(nameList[j][4], "%Y-%m-%dT%H:%M:%SZ")

                    # Calculate difference in seconds
                    time_diff = (time1_obj - time2_obj).total_seconds()

                    days_diff = time_diff / 86400

                    totalCount += 1
                    # write to file JourneyIDs here
                    message = "Found duplicate " + str(nameList[i][2]) + " and " + str(
                        nameList[j][2] + "\n" + "Result ID 1: " + str(nameList[j][3]) + "\t Result ID 2: " + str(
                            nameList[i][3]) + "\t Time Differential (Seconds): " + str(
                            round(time_diff, 2)) + "\t Time Differential (Days): " + str(round(days_diff, 2)) + "\n\n")
                    docNumberDuplicatesFile.write(message)
                    nameList[j][1] = random.randint(1, 100000000000)

    docNumberDuplicatesFile.write(("Total Duplicate Count: " + str(totalCount)))

    nameDobLogging = []
    for entry in nameList:
        fullnameAndDob = str(entry[0]) + str(entry[5])
        if fullnameAndDob not in nameDobLogging:
            nameDobLogging.append(fullnameAndDob)

    uniqueCounts = len(nameDobLogging)

    docNumberDuplicatesFile.write(("\n******************************\nUnique Entities Count: " + str(uniqueCounts)))
    docNumberDuplicatesFile.close()

def getCookie(url, username, password):
    # Generate Scanning Token

    url = url + "/token"

    print("Username:", username)
    print("Password: ", password)
    payload = "username=" + username + "&password=" + password + "&grant_type=password&area=scanning"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'csrftoken=lZ%2Fozo8esruwwKbaNtkpdnNLbIQQJ%2BOvl7%2Bly%2FaAxnauj7AFT9%2BDhAlcd5%2BypiAln8jmsBS5KXMI7npMo8RImc5SnHU8hsR0mA3Ji4hc64KwYs1GeIPMBEzi7G%2Bh8FWB2amAUSSI%2BFRcevnFmGGeSCC%2Bqi4xu1L5%2Bseirwn68YUs2at6hzqE0XXDNo3cJU9Iq9P6vuiy6wHHi3LtWKlXBAWp5HTi69WKfOrp8EdbagQvAgKJ0If0FoqL%2F341Ni6b5X8rB8Ddvr%2Bpa%2FJmfNG8iFPOefRUDVdJ19uI9eVGhRvmNK9kLzGtEK8rgiK0TSN%2BkL0CZ7%2FS%2BJBQAAaddhEWCGtj3r8P7n6IkVp%2F6F3yBxPmOsg%2B5jgPIr1gTumNGKPiZVfVvMrioHR77kj3eXmx6G5fJ72IOCEISMAjTvstwBWnoPwK4%2BJhSfOzLOvX1FNDqI0ICLMmi3SqMxvrWn%2FgPjBzeN5zRsguv8I6Z2%2Br%2BOynk2%2B%2BeOanuMhSRT2fahJ8pib%2F94gz61z1NlWH9zh3i5vr57FhdaJAxjAQbS7golMAcV22fJ4FeHmMY66FIWRRX%2FdSn7EOHaZMmZ1q6JcODaS%2F1eS2G7r%2Bu1YJiC6s32ahl6lpwBF5FwioEr2K%2FRH8CSptUKqexXUIxWSlhduuutejD4TsNvq9kdQPzfjm2M5t2agByXOX8zjq3dp3W3J3WD8lUvKQ6IYNTDdHMdzc%2Btq%2Btueqw7UdXs7Ztqfr4jLFP5gogyGsV4qEENlRUK8rKveXSUG5sj458ewtQ9YcqDIA49VEdunkz2ang%2BmRQd7B5n0h5umIFiCUedq6fBRsxpSy7Rxef07csMKZnfoUiQ%2Fw%2BWO%2Bq%2FjpM80tSno0i8RbVcavfUITmKn1Z%2FcmAWu3; incap_ses_454_2350164=ULusfVooUgT/V7xgA+9MBpqNH2EAAAAAKPfSjNQyQ7VizOJ9HAN7mg==; token=scTXhJagzfCS7TU-0rccBG1CaChUfsg_nmFhFOovuPnc-2khLyU0h4dkwDREObwBRgHB7AvfE-FTn6kemcs6KDs0oESXgVRgxwSHMn6HZZ87zFHTvjH_LpcwwzPA0eneXPGFHjPZPJTqtPcwRLMF0jGgSxb6SV-KCBBTuHdHzXBzHeQPieY5Jm0aK3gca5rVBzn55GnC-i5pdValUvRn7_nnlw-wSA1VU0yQi1U3jQ0b5_NKltR2XuxQIROHgUTizAmL32l1zKV0-cH0s7CQhu2OI1KV6sw-dEjSnUMc1JyBOSdLp-lScsdq0pqP3yV1lM5MI8K2ZIao49HJH8x-_WFW27rviWw4N-LNd09EAx7_yhDyHpYrpz2ZHrTE971X7fJKYioIr-UCjuXvgN-_ctsHuzWCiMO3zNHa2UZTC3bXKl7aRrP4uFcG3qUpJO8Hvq06CtHuouDnOC1U3tt1NoodhgK8U_05prdUmYOCRa_suWHDu2pbj6FRtGCYjyeKpwrBtSdpp3ysnZxednRniAwoKnwCVnU-7y-sYmvqPwc6lk-TQg95ZWAzMwGykNYyLfVsKe8XecbW4NJobdGa5djcCFHU5T_QqjhQ9IZUw4Y; visid_incap_2350164=l52W4pcqRxOTVVcR9PFVGNGKKmAAAAAAQUIPAAAAAADkv2ABJKY+/9k7pLuMjr2Y'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    cookie = response.json().get("access_token")

    test = (response.headers.get("Set-Cookie"))

    newTest = test.split(",")

    csrf = ""
    vis = ""
    incap = ""
    token = ""

    for x in newTest:
        if "csrf" in x:
            csrf = x
        if "visid" in x:
            vis = x
        if "incap_ses" in x:
            incap = x
        if (x[1] == 't' and x[2] == 'o') or (x[0] == 't' and x[1] == 'o'):
            token = x

    csrf = csrf.split(';')[0].replace(" ", "")
    vis = vis.split(';')[0].replace(" ", "")
    incap = incap.split(';')[0].replace(" ", "")
    token = token.split(';')[0].replace(" ", "")

    if len(vis) > 1:
        securityHeaders = csrf + ';' + incap + ';' + token + ';' + vis
    else:
        securityHeaders = csrf + ';' + incap + ';' + token

    '''
    print("CSRF: ", csrf)
    print("VIS: ", vis)
    print("INCAP:", incap)
    print("TOKEN: ", token)
    '''

    # print("Security Headers: ", securityHeaders)

    return [cookie, securityHeaders]


def generateMonthCSVFile(days, csvName, url, cookie, securityHeaders):
    current_time = datetime.datetime.now()
    dateFormatCurrent = str(current_time.day) + "/" + str(current_time.month) + "/" + str(current_time.year)

    a_date = datetime.date(current_time.year, current_time.month, current_time.day)
    days = datetime.timedelta(days)

    new_date = a_date - days
    dateFormatNew = str(new_date.day) + "/" + str(new_date.month) + "/" + str(new_date.year)


    req = url + "/Search/ExportEntries?searchrequest=%7B%22DataPagingCriteria%22:%7B%22ResultItemsStartIndex%22:0,%22ResultItemsCount%22:15%7D,%22EvaluatedPersonEntrySearchCriteria%22:%7B%22EntryDateTimeMax%22:%22" + dateFormatCurrent + "%2023:59:59%22,%22EntryDateTimeMin%22:%22" + dateFormatNew + "%22,%22HighLevelResult%22:null,%22PersonEntryMetaDatas%22:[],%22ScanReason%22:null,%22AdditionalDataFilters%22:null,%22DecisionOrigin%22:null,%22KeywordSearchCriteria%22:%7B%22KeywordValue%22:null,%22KeywordValueForReference%22:null%7D,%22AdditionalDataNames%22:[%22BranchCode%22,%22UserName%22,%22CustomerNumber%22,%22IsMarkedForSecondLineReview%22,%22IsCommited%22,%22IsExported%22,%22ManualFaceMatchResult%22,%22AutomatedFaceMatchResult%22,%22LivenessFinalResult%22,%22LivenessFramesNumber%22,%22LivenessActionsNumber%22,%22LivenessActionTimeout%22,%22LivenessNumberOfSelfie%22,%22LivenessJumpsAllowed%22,%22LivenessPassedFrames%22,%22Site%22,%22Location%22]%7D,%22UserId%22:null%7D"
    print(req)

    payload = {}
    headers = {
        'Authorization': cookie,
        'Cookie': securityHeaders
    }
    response = requests.request("GET", req, headers=headers, data=payload)
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        with open(csvName, 'w') as out:
            out.write("")
    else:
        with open(csvName, 'w') as out:
            out.write(response.text)


def runAPIs(data_chunk, cookie, securityHeaders, url):

    def getRetrieveResponse():
        try:
            newURL = url + "/journey/get?journeyID=" + ID
            payload = {}
            headers = {
                'Cookie': cookie + '; ' + securityHeaders,
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", newURL, headers=headers, data=payload)
            return response
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            line_number = tb[-1].lineno
            print("Data grab fail:", e)
            print(f"Exception occurred on line: {line_number}")

    def getEvalResponse():
        try:
            newURL = url + "/Search/GetEvaluatedPersonEntryValidationResults?id=" + ID
            payload = {}
            headers = {
                'Cookie': cookie + '; ' + securityHeaders,
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", newURL, headers=headers, data=payload)
            return response
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            line_number = tb[-1].lineno
            print("Data grab fail:", e)
            print(f"Exception occurred on line: {line_number}")


    for ID in data_chunk:

        print("Processing: " + str(Loader.currentLoaderCount) + "/" + str(Loader.loaderTotal))



        Loader.currentLoaderCount += 1

        responseDetails = getRetrieveResponse()

        #print(responseDetails.text)

        individualResults = []
        #file = open(name + "_timingLogs.txt", "a")

        # Manufacturer, Model, OS Version and Connectivity
        manufacturerUsed = "Manufacturer_NULL"
        modelUsed = "Model_NULL"
        OSUsed = "OS_Version_NULL"
        connectivityUsed = "Connectivity_NULL"
        nfcState = "NFC_STATE_NULL"
        mjcsVersion = "MJCS_VERSION_NULL"
        appID = "MJCS_ID_NULL"

        try:
            if responseDetails.status_code == 200:
                response = responseDetails.json()

                #Get HLR
                highLevelResult = "RESULT_NULL"
                try:
                    highLevelResult = response.get("HighLevelResult")
                except:
                    print("HLR Failed to GET")

                if imageAnalysis == "y":
                    journeyImages = response.get("JourneyImages")

                    try:
                        attempt = 0
                        downloadURL = "null"
                        for journeyImage in journeyImages:
                            if journeyImage.get("StepName") == "ID Document" and journeyImage.get("ImageRole") == "WhiteImage" and journeyImage.get("Attempt") > attempt:
                                attempt = journeyImage.get("Attempt")
                                downloadURL = journeyImage.get("ImageUrl")

                        if downloadURL != "null":

                            payload = {}
                            headers = {
                                'Authorization': cookie,
                                'Cookie': securityHeaders
                            }

                            responseImage = requests.request("GET", downloadURL, headers=headers, data=payload)

                            imageName = ID+"-front.jpg"

                            with open('imageStoreDocuments/'+imageName, 'wb') as f:
                                f.write(responseImage.content)

                            '''
                            IMAGE ANALYSIS HERE
                            '''
                    except:
                        print("Falied Record", ID, "For JourneyImages Downloading")

                #Get Overriden Result
                overriddenResult = "OVERRIDEN_NULL"
                try:
                    if response.get("LastDecision").get("Origin") == "ManualOverride":
                        if response.get("LastDecision").get("DecisionCode") == "Accepted":
                            overriddenResult = "Accepted"
                        if response.get("LastDecision").get("DecisionCode") == "Rejected":
                            overriddenResult = "Rejected"
                except:
                    print("Falied Record", ID, "For Overriden Logging")
                    overriddenResult = "PROGRAM ERROR"


                #Get facematch score
                facematchScore ="FM_SCORE_NULL"
                try:
                    for item in response.get("ProcessedDocuments"):
                        if "FaceMatchConfidenceScore" in item:
                            facematchScore = item.get("FaceMatchConfidenceScore")
                except:
                    print("Failed FM")

                #Get Triple Scan Attempts
                attempts = 1
                try:
                    if response.get("JourneySteps")[0].get("TripleScanAttempts") is not None:
                        if response.get("JourneySteps")[0].get("TripleScanAttempts") == "2":
                            attempts = 2
                        elif response.get("JourneySteps")[0].get("TripleScanAttempts") == "3":
                            attempts = 3
                except Exception:
                    pass


                #Get Browser and Platform
                browserUsed = "BROWSER_NULL"
                platformUsed = "PLATFORM_NULL"
                metadata = response.get("MetaData")
                try:
                    for responseContent in metadata:
                        if responseContent.get("Name") == "Platform" or responseContent.get("Name") == "MJCS_METADATA_PLATFORM":
                            platformUsed = responseContent.get("Value").lower()
                        if responseContent.get("Name") == "Browser":
                            browserUsed = responseContent.get("Value").lower()
                except:
                    print("Error with browser")


                try:
                    for responseContent in metadata:
                        if responseContent.get("Name") == "MJCS_METADATA_APP_ID":
                            appID = responseContent.get("Value").lower()
                        if responseContent.get("Name") == "MJCS_METADATA_MJCS_VERSION":
                            mjcsVersion = responseContent.get("Value").lower()
                except:
                    print("Error with browser")


                #Get Country, Doc Type and Scan Time
                country = "COUNTRY_NULL"
                doctype = "Other"
                scanTime = "SCANTIME_NULL"
                processedDocs = response.get("ProcessedDocuments")

                for processedDoc in processedDocs:
                    if "IssuingCountryName" in processedDoc:
                        country = processedDoc.get("IssuingCountryName")
                        if "DocumentType" in processedDoc:
                            doctype = processedDoc.get("DocumentType")
                        if "ScanDateTime" in processedDoc:
                            scanTime = processedDoc.get("ScanDateTime")

                #Get Dropout Stage (Undefined)
                dropoutStage = "ACTION_NULL"
                if "RequiredAction" in response:
                    currentAction = response.get("RequiredAction")
                    dropoutStage = currentAction



                #same as usual except ignore when overriddenResult
                totalJourneyTime = "NaN"
                if overriddenResult == "OVERRIDEN_NULL":
                    try:
                        if highLevelResult != "Undefined":
                            from datetime import datetime
                            InitiatedDateTime = response.get("InitiatedDateTime")
                            DecisionDateTime = response.get("LastDecision").get("DecisionDateTime")
                            initiated_datetime = datetime.fromisoformat(InitiatedDateTime)
                            decision_datetime = datetime.strptime(DecisionDateTime, "%d/%m/%Y %H:%M:%S")
                            # calculate the time difference
                            time_difference = decision_datetime - initiated_datetime
                            totalJourneyTime = time_difference.total_seconds()
                    except:
                        print("Error with calculating total journey time")


                try:
                    for responseContent in metadata:
                        if responseContent.get("Name") == "MJCS_METADATA_DEVICE_MANUFACTURER":
                            manufacturerUsed = responseContent.get("Value").lower()
                        if responseContent.get("Name") == "MJCS_METADATA_DEVICE_MODEL":
                            modelUsed = responseContent.get("Value")

                            iPhoneModelDict = {
                                "iPhone9,1" : "iPhone 7",
                                "iPhone9,2" : "iPhone 7 Plus",
                                "iPhone9,3" : "iPhone 7",
                                "iPhone9,4" : "iPhone 7 Plus",
                                "iPhone10,1" : "iPhone 8",
                                "iPhone10,2" : "iPhone 8 Plus",
                                "iPhone10,3" : "iPhone X Global",
                                "iPhone10,4" : "iPhone 8",
                                "iPhone10,5" : "iPhone 8 Plus",
                                "iPhone10,6" : "iPhone X GSM",
                                "iPhone11,2" : "iPhone XS",
                                "iPhone11,4" : "iPhone XS Max",
                                "iPhone11,6" : "iPhone XS Max Global",
                                "iPhone11,8" : "iPhone XR",
                                "iPhone12,1" : "iPhone 11",
                                "iPhone12,3" : "iPhone 11 Pro",
                                "iPhone12,5" : "iPhone 11 Pro Max",
                                "iPhone12,8" : "iPhone SE 2nd Gen",
                                "iPhone13,1" : "iPhone 12 Mini",
                                "iPhone13,2" : "iPhone 12",
                                "iPhone13,3" : "iPhone 12 Pro",
                                "iPhone13,4" : "iPhone 12 Pro Max",
                                "iPhone14,2" : "iPhone 13 Pro",
                                "iPhone14,3" : "iPhone 13 Pro Max",
                                "iPhone14,4" : "iPhone 13 Mini",
                                "iPhone14,5" : "iPhone 13",
                                "iPhone14,6" : "iPhone SE 3rd Gen",
                                "iPhone14,7" : "iPhone 14",
                                "iPhone14,8" : "iPhone 14 Plus",
                                "iPhone15,2" : "iPhone 14 Pro",
                                "iPhone15,3" : "iPhone 14 Pro Max",
                                "iPhone15,4" : "iPhone 15",
                                "iPhone15,5" : "iPhone 15 Plus",
                                "iPhone16,1" : "iPhone 15 Pro",
                                "iPhone16,2" : "iPhone 15 Pro Max"
                            }

                            # Check if the modelUsed is in the dictionary and replace if it is
                            if modelUsed in iPhoneModelDict:
                                modelUsed = iPhoneModelDict[modelUsed]



                        if responseContent.get("Name") == "MJCS_METADATA_OS_VERSION":
                            OSUsed = responseContent.get("Value").lower()
                        if responseContent.get("Name") == "MJCS_METADATA_CONNECTIVITY":
                            connectivityUsed = responseContent.get("Value").lower()
                        if responseContent.get("Name") == "NfcState":
                            nfcStateUsed = responseContent.get("Value")
                except:
                    print("Error with device stats")

                individualResults.append(ID)
                individualResults.append(highLevelResult)
                individualResults.append(overriddenResult)
                individualResults.append(facematchScore)
                individualResults.append(attempts)
                individualResults.append(browserUsed)
                individualResults.append(platformUsed)
                individualResults.append(country)
                individualResults.append(doctype)
                individualResults.append(scanTime)
                individualResults.append(dropoutStage)
                individualResults.append(totalJourneyTime)



            else:
                print(responseDetails.status_code)
            # API 1 COMPLETED

            responseDetailsEval = getEvalResponse()
            if responseDetailsEval.status_code == 200:
                responseEval = responseDetailsEval.json()


                livenessTime = "NaN"
                autocaptureTime = "NaN"
                autoCaptureUsed = False
                manualCaptureUsed = False
                fileUploadUsed = False
                metadata = responseEval.get("MetaData")
                journeySteps = responseEval.get("JourneySteps")
                livenessScore = -1
                livenessFailReason = -1
                expiryDate = "NULL"
                docName = "NULL"
                firstName = "NULL"
                middleName = "NULL"
                lastName = "NULL"

                if 'DocumentName' in responseEval:
                    docName = responseEval.get("DocumentName")

                if 'ExpiryDate' in responseEval:
                    expiryDate =responseEval.get("ExpiryDate")

                if 'FirstName' in responseEval:
                    firstName =responseEval.get("FirstName")
                if 'MiddleName' in responseEval:
                    middleName =responseEval.get("MiddleName")
                if 'LastName' in responseEval:
                    lastName =responseEval.get("LastName")

                if 'LivenessActionsDetails' in responseEval:
                    try:
                        livenessActionDetails = responseEval.get("LivenessActionsDetails")[0]
                        if 'Score' in livenessActionDetails:
                            livenessScore = livenessActionDetails.get("Score")

                        if 'FailureReason' in livenessActionDetails:
                            livenessFailReason = livenessActionDetails.get("FailureReason")
                    except:
                        livenessScore = -1
                        livenessFailReason = -1


                for responseContent in metadata:
                    if responseContent.get("Name") == "Liveness: Total time":  # Same on both WSDK and MJCS
                        livenessTime = responseContent.get("Value")
                        livenessTime = livenessTime.replace(",", ".")
                        livenessTime = round(float(livenessTime), 0) / 1000

                    if responseContent.get("Name") == "SC: Length of Smart Capture":
                        autocaptureTime = responseContent.get("Value")
                        autocaptureTime = autocaptureTime.replace(",", ".")
                        autocaptureTime = round(float(autocaptureTime), 0) / 1000


                    if responseContent.get("Name") == "MJCS_METADATA_SMART_CAPTURE_TIME":
                        autocaptureTime = responseContent.get("Value")
                        autocaptureTime = autocaptureTime.replace(",", ".")
                        autocaptureTime = round(float(autocaptureTime) * 1000, 0) / 1000


                    if responseContent.get("Name") == "Capture Type":
                        if responseContent.get("Value") == "File Upload":
                            fileUploadUsed = True

                    if responseContent.get("Name") == "Capture Type":
                        if responseContent.get("Value") == "Manual Capture":
                            manualCaptureUsed = True

                    if responseContent.get("Name") == "MJCS_METADATA_CAPTURE_METHOD":
                        if responseContent.get("Value") == "MANUAL_CAPTURE":
                            manualCaptureUsed = True

                if not manualCaptureUsed and not fileUploadUsed:
                    autoCaptureUsed = True


                validationDetails = responseEval.get("ValidationDetails")

                personalAuthFlags = []

                for responseContent in validationDetails:
                    if responseContent.get("Result") == 2:
                        personalAuthFlags.append(responseContent.get("Name"))
                        found = False
                        for flag in authFlags:
                            if responseContent.get("Name") in flag:
                                flag[1] += 1
                                found = True

                        if not found:
                            authFlags.append([responseContent.get("Name"), 1])

                personalAuthFlags = str(personalAuthFlags)

                blur = False
                glare = False
                res = False
                noDoc = False

                qualityCheckDetails = responseEval.get("QualityCheckDetails")
                for responseContent in qualityCheckDetails:
                    if responseContent.get("State") == 2:
                        if responseContent.get("Name") == "BlurCheck":
                            blur = True
                        if responseContent.get("Name") == "GlareCheck":
                            glare = True
                        if responseContent.get("Name") == "LowResolutionCheck":
                            res = True
                        if responseContent.get("Name") == "FullDocumentInViewCheck":
                            noDoc = True



                ageRange = "AGE_NO_DATA"
                try:
                    age = int(responseEval.get("Age"))
                    if age >= 90:
                        ageRange = "90+"
                    elif age >= 80:
                        ageRange = "80-89"
                    elif age >= 70:
                        ageRange = "70-79"
                    elif age >= 60:
                        ageRange = "60-69"
                    elif age >= 50:
                        ageRange = "50-59"
                    elif age >= 40:
                        ageRange = "40-49"
                    elif age >= 30:
                        ageRange = "30-39"
                    elif age >= 20:
                        ageRange = "20-29"
                    elif age >= 10:
                        ageRange = "10-19"
                except:
                    pass


                journeyDef = "JOURNEYDEF_NULL"
                usernameOfScanner = "USERNAME_NULL"
                try:
                    additionalData = responseEval.get("AdditionalData")
                    for check in additionalData:
                        if check.get("Name") == "journeyDefinitionName":
                            journeyDef = check.get("Value")
                        if check.get("Name") == "UserName":
                            usernameOfScanner = check.get("Value")

                except:
                    pass



                frontsideResult = "N/A"
                backsideResult = "N/A"
                POAResult = "N/A"
                nfcResult = "N/A"
                nfcCrossResult = "N/A"
                livenessResult = "N/A"
                selfieResult = "N/A"
                dataResult = "N/A"


                for responseContent in journeySteps:
                    if responseContent.get("Type") == "FRONTSIDE":
                        if responseContent.get("HighLevelResult") == "Passed":
                            frontsideResult = "Passed"
                        elif responseContent.get("HighLevelResult") == "Refer":
                            frontsideResult = "Refer"
                        elif responseContent.get("HighLevelResult") == "NOTPROVIDED" or responseContent.get("HighLevelResult") == "Undefined":
                            frontsideResult = "Undefined"
                        else:
                            frontsideResult = "Other"

                    if responseContent.get("Type") == "BACKSIDE":
                        if responseContent.get("HighLevelResult") == "Passed":
                            backsideResult = "Passed"
                        elif responseContent.get("HighLevelResult") == "Refer":
                            backsideResult = "Refer"
                        elif responseContent.get("HighLevelResult") == "NOTPROVIDED" or responseContent.get(
                                "HighLevelResult") == "Undefined":
                            backsideResult = "Undefined"
                        else:
                            backsideResult = "Other"

                    if responseContent.get("Type") == "ADDRESS_DOCUMENT":
                        if responseContent.get("HighLevelResult") == "Passed":
                            POAResult = "Passed"
                        elif responseContent.get("HighLevelResult") == "Refer":
                            POAResult = "Refer"
                        elif responseContent.get("HighLevelResult") == "NOTPROVIDED" or responseContent.get(
                                "HighLevelResult") == "Undefined":
                            POAResult = "Undefined"
                        else:
                            POAResult = "Other"

                    if responseContent.get("Type") == "NFC":
                        if responseContent.get("HighLevelResult") == "Passed":
                            nfcResult = "Passed"
                        elif responseContent.get("HighLevelResult") == "Refer":
                            nfcResult = "Refer"
                        elif responseContent.get("HighLevelResult") == "NOTPROVIDED" or responseContent.get(
                                "HighLevelResult") == "Undefined":
                            nfcResult = "Undefined"
                        elif responseContent.get("HighLevelResult") == "Skipped" or responseContent.get(
                                "HighLevelResult") == "Skipped":
                            nfcResult = "Skipped"
                        else:
                            nfcResult = "Other"

                    if responseContent.get("Type") == "NFC Cross-Check":
                        if responseContent.get("HighLevelResult") == "Passed":
                            nfcCrossResult = "Passed"
                        elif responseContent.get("HighLevelResult") == "Refer":
                            nfcCrossResult = "Refer"
                        elif responseContent.get("HighLevelResult") == "NOTPROVIDED" or responseContent.get(
                                "HighLevelResult") == "Undefined":
                            nfcCrossResult = "Undefined"
                        elif responseContent.get("HighLevelResult") == "Skipped" or responseContent.get(
                                "HighLevelResult") == "Skipped":
                            nfcCrossResult = "Skipped"
                        else:
                            nfcCrossResult = "Other"

                    if responseContent.get("Type") == "LIVENESS":
                        if responseContent.get("HighLevelResult") == "Passed":
                            livenessResult = "Passed"
                        elif responseContent.get("HighLevelResult") == "Refer":
                            livenessResult = "Refer"
                        elif responseContent.get("HighLevelResult") == "NOTPROVIDED" or responseContent.get(
                                "HighLevelResult") == "Undefined":
                            livenessResult = "Undefined"
                        else:
                            livenessResult = "Other"

                    if responseContent.get("Type") == "SELFIE":
                        if responseContent.get("HighLevelResult") == "Passed":
                            selfieResult = "Passed"
                        elif responseContent.get("HighLevelResult") == "Refer":
                            selfieResult = "Refer"
                        elif responseContent.get("HighLevelResult") == "NOTPROVIDED" or responseContent.get(
                                "HighLevelResult") == "Undefined":
                            selfieResult = "Undefined"
                            livenessResult = "Undefined"
                        else:
                            selfieResult = "Other"

                    if responseContent.get("Type") == "ADDITIONALDATA":
                        if responseContent.get("HighLevelResult") == "Passed":
                            dataResult = "Passed"
                        elif responseContent.get("HighLevelResult") == "Refer":
                            dataResult = "Refer"
                        elif responseContent.get("HighLevelResult") == "NOTPROVIDED" or responseContent.get(
                                "HighLevelResult") == "Undefined":
                            dataResult = "Undefined"
                        else:
                            dataResult = "Other"





                individualResults.append(livenessTime)
                individualResults.append(autocaptureTime)
                individualResults.append(autoCaptureUsed)
                individualResults.append(manualCaptureUsed)
                individualResults.append(fileUploadUsed)
                individualResults.append(blur)
                individualResults.append(glare)
                individualResults.append(res)
                individualResults.append(noDoc)
                individualResults.append(ageRange)
                individualResults.append(journeyDef)
                individualResults.append(usernameOfScanner)
                individualResults.append(frontsideResult)
                individualResults.append(backsideResult)
                individualResults.append(POAResult)
                individualResults.append(nfcResult)
                individualResults.append(livenessResult)
                individualResults.append(selfieResult)
                individualResults.append(dataResult)
                individualResults.append(manufacturerUsed)
                individualResults.append(modelUsed)
                individualResults.append(OSUsed)
                individualResults.append(connectivityUsed)
                individualResults.append(nfcCrossResult)
                individualResults.append(nfcState)
                individualResults.append(livenessScore)
                individualResults.append(livenessFailReason)
                individualResults.append(expiryDate)
                individualResults.append(docName)
                individualResults.append(firstName)
                individualResults.append(middleName)
                individualResults.append(lastName)
                individualResults.append(personalAuthFlags)
                individualResults.append(mjcsVersion)
                individualResults.append(appID)

                clientResults.append(individualResults)


        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            line_number = tb[-1].lineno
            print("Data grab fail:", e)
            print(f"Exception occurred on line: {line_number}")


            #file.close()





for client in reportingClients:
    name = client.get("name")
    username = client.get("username")
    password = client.get("password")
    days = client.get("days")
    url = client.get("url")
    imageAnalysis = client.get("imageAnalysis")
    threads = client.get("threads")
    override = client.get("override")
    overrideName = client.get("overrideName")
    dedupeActive = client.get("dedupe")

    Loader.currentLoaderCount = 0

    try:
        authFlags = []

        clientResults = []

        # Create New Directory If Customer Doesn't Exist
        currentCustomerDir = "Reports/"+name
        root_directory = os.getcwd()
        directory_path = os.path.join(root_directory, currentCustomerDir)
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
            print(f"Directory '{directory_name}' created in {root_directory}")
        else:
            print(f"Directory '{directory_name}' already exists in {root_directory}")


        # Create New Month Dir In The Customer Dir
        current_date = datetime.datetime.now()
        month_name = current_date.strftime("%B")

        currentMonthDir = currentCustomerDir + "/"+ month_name
        root_directory = os.getcwd()
        directory_path = os.path.join(root_directory, currentMonthDir)
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
            print(f"Directory '{directory_name}' created in {root_directory}")
        else:
            print(f"Directory '{directory_name}' already exists in {root_directory}")

        content = getCookie(url, username, password)
        cookie = content[0]
        securityHeaders = content[1]

        # Download CSV file

        downloaded = False
        csv_file_name = name + month_name + ".csv"
        if override:
            downloaded = True
            csv_file_name = overrideName


        while not downloaded:
            generateMonthCSVFile(days, csv_file_name, url, cookie, securityHeaders)
            with open(csv_file_name, "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                is_empty = not any(row for row in csv_reader)
            if is_empty:
                print(f"The CSV file '{csv_file_name}' is empty.")
                days -= 2
                print("Trying ",days, " days")
            else:
                print(f"The CSV file '{csv_file_name}' is not empty.")
                downloaded = True

        if dedupeActive:
            dedupe()

        journeyIDs = []

        with open(csv_file_name, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                ids = row[0]
                journeyIDs.append(ids)

        journeyIDs.pop(0)





        print("JourneyIDs:", journeyIDs)

        Loader.loaderTotal = len(journeyIDs)


        results = []

        split_arr = []
        split_size = len(journeyIDs) // threads  # integer division
        split_remainder = len(journeyIDs) % threads

        start = 0
        for i in range(threads):
            end = start + split_size + (i < split_remainder)
            split_arr.append(journeyIDs[start:end])
            start = end

        # Thread

        process_threads = []
        for i in range(threads):
            thread = threading.Thread(target=runAPIs, args=(split_arr[i], cookie, securityHeaders, url,))
            process_threads.append(thread)

        # Start each thread
        for thread in process_threads:
            thread.start()

        # Wait for all threads to finish
        for thread in process_threads:
            thread.join()

        authFileName = currentMonthDir+"/AuthFlags.txt"
        file = open(authFileName, "w")
        for authCheck in authFlags:
            file.write(str(authCheck)+"\n")
        file.close()

        dupeByDocNo(csv_file_name ,currentMonthDir)

        if os.path.exists(csv_file_name):
            os.remove(csv_file_name)

        with open(currentMonthDir + '/DataVisualisation.csv', 'w', newline='') as file:

            # Create a CSV writer object
            writer = csv.writer(file)

            # Write the header row to the CSV file
            writer.writerow(vizHeader)



            for row in clientResults:
                if len(row) == len(vizHeader):
                    writer.writerow(row)
                else:
                    print("Row length not the same when writing to DataViz file")




        with open(currentCustomerDir + '/DataVisualisation.csv', 'w', newline='') as file:

            # Create a CSV writer object
            writer = csv.writer(file)

            # Write the header row to the CSV file
            writer.writerow(vizHeader)

            for row in clientResults:
                if len(row) == len(vizHeader):
                    writer.writerow(row)
                else:
                    print("Row length not the same when writing to DataViz file")


        archive_name = os.path.join(currentMonthDir, "documentImages")
        shutil.make_archive(archive_name, 'zip', "./imageStoreDocuments")
        print(f"Archive saved as {archive_name}.zip")

        # Delete contents in the directory
        for filename in os.listdir("./imageStoreDocuments"):
            file_path = os.path.join("./imageStoreDocuments", filename)

            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)  # remove the file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # remove dir
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")






        print(name, " completed")

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1].lineno
        print("Data grab fail:", e)
        print(f"Exception occurred on line: {line_number}")
        print("Failed" + name)
        file = open("FailureLogging.txt", "a")
        file.write(name+" failed")
        file.close()





