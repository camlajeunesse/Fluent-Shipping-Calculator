# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import PySimpleGUI as sg
import pandas as pd
import numpy as np
import re
import subprocess



def addLeadingZeros(zipRaw: int):
    aString = str(zipRaw)
    if (zipRaw < 10000):
        aString = "0" + aString

    if (zipRaw < 1000):
        aString = "0" + aString

    if (zipRaw < 100):
        aString = "0" + aString

    if (zipRaw < 10):
        aString = "0" + aString

    return aString


df = pd.read_csv("FedExZones.csv")
df2 = pd.DataFrame()

newRows = []
for i, row in df.iterrows():
    startZip = int(row[0].split("-")[0])
    endZip = int(row[0].split("-")[-1])



    for zipCode in np.arange(startZip, endZip + 1):
        newRows.append([addLeadingZeros(zipCode)] + [row[1]])

df2 = pd.DataFrame(data=newRows, columns=['zips', 'zones'])

import csv


df2.set_index('zips')
dfground = pd.read_csv("ground.csv")
dfexpress = pd.read_csv("express.csv")
df2day = pd.read_csv("2day.csv")
dfovernight = pd.read_csv("overnight.csv")
dfcaneconomy = pd.read_csv("InternationalEconomy.csv")
dfcanpriority = pd.read_csv("InternationalPriority.csv")

def findPackage(itemqtys):
    returnVal = []
    aQty = 0
    dQty = 0
    aMass = 0
    dMass = 0
    i = 0
    oneandthree = itemqtys[0] + itemqtys[2]
    while i < oneandthree:
        aMass += 1
        if aMass == 4:
            aMass = 0
            aQty += 1
        i += 1
    i = 0
    while i < itemqtys[1]:
        returnVal.append('b')
        i += 1

    cCount = itemqtys[3] + itemqtys[5] + itemqtys[10]
    i = 0
    while i < cCount:
        returnVal.append('c')
        i += 1
    i = 0
    while i < itemqtys[4]:
        aMass += 2
        if aMass >= 4:
            aMass -= 4
            aQty += 1
        i += 1
    i = 0

    gMass = 0
    gQty = 0
    i = 0
    while i < itemqtys[13]:
        gMass += 1
        if gMass == 2:
            gMass = 0
            gQty += 1
        i += 1
    modularMass = itemqtys[6] + itemqtys[8] + itemqtys[9] + itemqtys[11] + itemqtys[12]
    while modularMass > 0 and aMass > 0:
        aMass += 1
        modularMass -= 1
        if aMass == 4:
            aQty += 1
            aMass = 0

    while modularMass > 0:
        dMass += 1
        if dMass == 4:
            dQty += 1
            dMass = 0
        modularMass -= 1
    if aMass > 0:
        aQty += 1
    if dMass > 0:
        dQty += 1
    if gMass > 0:
        gQty += 1
    i = 0
    while i < gQty:
        returnVal.append('g')
        i += 1
    i = 0
    while i < aQty:
        returnVal.append('a')
        i += 1
    i = 0
    while i < dQty:
        returnVal.append('d')
        i += 1
    if aQty == 0 and dQty == 0 and itemqtys[7] > 0:
        returnVal.append('e')
    if aQty == 0 and dQty == 0 and gQty == 0:
        fQty = np.ceil((itemqtys[14] + itemqtys[15]) / 3)
        i = 0
        while i < fQty:
            returnVal.append('f')
            i += 1

    return returnVal


def findZone(zipCode):
    val = df2.loc[df2['zips'] == zipCode, 'zones'].values[0]
    return int(val)


def numberifyBoxes(packages):
    returnval = []
    for package in packages:
        match package:
            case 'a':
                returnval.append(55)
            case 'b':
                returnval.append(30)
            case 'c':
                returnval.append(20)
            case 'd':
                returnval.append(30)
            case 'e':
                returnval.append(10)
            case 'f':
                returnval.append(5)
            case 'g':
                returnval.append(15)
    return returnval

def priceBox(sFormat, weight, zone, canada):
    if sFormat == "International Priority" and canada:
        return float(dfcanpriority.iloc[weight-1, 1])
    if canada:
        return float(dfcaneconomy.iloc[weight-2, 1])
    if sFormat == "Two Day":
        return float(df2day.iloc[weight-1, zone - 1])
    if sFormat == "Ground":
        return float(dfground.iloc[weight, 1])
    if sFormat == "Standard Overnight":
        return float(dfovernight.iloc[weight-1, zone - 1])
    return float(dfexpress.iloc[weight-1, zone - 1])

def Handling(packages, items):
    returnval = 8
    costPerItem = 4
    for package in packages:
        if package == 'a' or package == 'd':
            returnval+= 17
        if package == 'b' or package == 'c':
            returnval+= 25
        else:
            returnval+= 12.5
    for item in items:
        returnval+= item * costPerItem
    return returnval

def calShipping(packages, zone, override, canada, zipCode):
    format = pickFormat(zone, override, canada, zipCode)
    returnval = 0.0
    for weight in numberifyBoxes(packages):
        returnval += priceBox(format, weight, zone, canada)
    returnval *= .46

    for package in packages:
        if package == 'a' or package == 'd' or package == 'e':
            returnval += 6.55
    return returnval


def pickFormat(zone, override, canada, zipCode):

    if canada and override == "Priority":
            return "International Priority"
    if canada:
        return "International Economy"
    if override == "Express Saver":
        return "Express Saver"
    if override == "Two Day":
        return "Two Day"
    if override == "Priority":
        return "Standard Overnight"
    if CheckGround(zipCode):
        return "Ground"
    if zone < 6:
        return "Express Saver"
    return "Two Day"

def CheckGround(zipCode):
    LocalZips = []
    with open("Local.csv", 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            LocalZips.extend(row)

    if zipCode in LocalZips:
        return True
    return False

sg.theme('Dark Blue 3')
itemNames = ['T2 Full Kit               ', 'T2 Full Starter Kit       ', 'T20 Full Kit              ',
             'T20 Starter Kit           ', 'T100 Full Kit             ', 'T100 Starter Kit          ',
             'Nuclei Isolation Kit      ', 'UDI Kit                   ', 'Epitope Kit               ',
             'T2 A Kit                  ', 'T2 A Starter Kit          ', 'T20 A Kit                 ',
             'T100 A Kit                ', 'T2 Starter Expansion Kit  ', 'T20 Starter Expansion Kit ',
             'T100 Starter Expansion Kit']

font = ('Courier', 12)

inputcolumn = [[sg.Text('QTY ' + itemNames[0], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-0', enable_events=True)],
               [sg.Text('QTY ' + itemNames[1], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-1', enable_events=True)],
               [sg.Text('QTY ' + itemNames[2], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-2', enable_events=True)],
               [sg.Text('QTY ' + itemNames[3], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-3', enable_events=True)],
               [sg.Text('QTY ' + itemNames[4], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-4', enable_events=True)],
               [sg.Text('QTY ' + itemNames[5], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-5', enable_events=True)],
               [sg.Text('QTY ' + itemNames[6], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-6', enable_events=True)],
               [sg.Text('QTY ' + itemNames[7], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-7', enable_events=True)],
               [sg.Text('QTY ' + itemNames[8], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-8', enable_events=True)],
               [sg.Text('QTY ' + itemNames[9], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-9', enable_events=True)],
               [sg.Text('QTY ' + itemNames[10], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-10', enable_events=True)],
               [sg.Text('QTY ' + itemNames[11], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-11', enable_events=True)],
               [sg.Text('QTY ' + itemNames[12], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-12', enable_events=True)],
               [sg.Text('QTY ' + itemNames[13], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-13', enable_events=True)],
               [sg.Text('QTY ' + itemNames[14], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-14', enable_events=True)],
               [sg.Text('QTY ' + itemNames[15], font=font), sg.InputText(default_text="0", font=font, key='-NUMZ-15', enable_events=True)]
               ]

l1 = sg.Column(inputcolumn)
l2 = sg.Text('Shipping Discount', font=font), sg.InputText(default_text="54", font=font)
l3 = sg.Text('Zip code', font=font), sg.InputText(default_text="02472", font=font, key='-NUMZ-16', enable_events=True), sg.Checkbox("Canada?", font=font, default=False, key="-CHECKBOX1-")
l4 = sg.Combo(["Auto Select", "Priority"], default_value="Auto Select", font=font,
              expand_x=True, enable_events=True, readonly=False, key='-COMBO-')
l5 = [sg.Button('Calculate', font=font), sg.Button('Close', font=font)]
l6 = [sg.Text('Total Price: ', font=font), sg.Text(key='price', font=font)]
l7 = [sg.Text('FedEx Price: ', font=font), sg.Text(key='FedExprice', font=font)]
l8 = [sg.Text('Shipping Type:   ', font=font), sg.Text(key='shippingType', font=font)]
l9 = [sg.Text('Handling:    ', font=font), sg.Text(key='handlingprice', font=font)]


layout = [[l1],
          [l3],
          [l4],
          [l5],
          [l7],
          [l9],
          [l6],
          [l8],
          ]
# Create the Window
window = sg.Window('Fluent Shipping Calculator', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, UIvalues = window.read()
    if event == sg.WIN_CLOSED or event == 'Close':  # if user closes window or clicks cancel
        break
    pattern = r'^-NUMZ-\d+$'
    if re.match(pattern,event):
        text = UIvalues[event]
        newVal=''
        for value in UIvalues[event]:
            if value in ('0123456789'):
                newVal+=value

        window[event].update(newVal)

    if event == 'Calculate':

        cleanItemQtyList = []
        for i in range(0, 16):
            if UIvalues['-NUMZ-'+str(i)]=='':
                cleanItemQtyList.append(0)
            else:
                cleanItemQtyList.append(int(UIvalues['-NUMZ-'+str(i)]))
        letterList=findPackage(cleanItemQtyList)
        zipCode = UIvalues['-NUMZ-'+str(16)]
        if UIvalues['-NUMZ-'+str(16)]=='':
            zipCode = "02472"
            
        FedExprice = calShipping(letterList, findZone(zipCode), UIvalues['-COMBO-'], UIvalues['-CHECKBOX1-'], zipCode)
        FedExprice = round(FedExprice, 2)
        FedExprice = "{:.2f}".format(FedExprice)
        strFedExprice = '  $' + str(FedExprice)
        window['FedExprice'].update(strFedExprice)

        handlingprice = Handling(letterList, cleanItemQtyList)
        handlingprice = round(handlingprice, 2)
        handlingprice = "{:.2f}".format(handlingprice)
        strhandlingprice = '+ $' + str(handlingprice)
        window['handlingprice'].update(strhandlingprice)

        pricy = calShipping(letterList, findZone(zipCode), UIvalues['-COMBO-'], UIvalues['-CHECKBOX1-'], zipCode)
        pricy += Handling(letterList, cleanItemQtyList)
        pricy = round(pricy, 2)
        pricy = "{:.2f}".format(pricy)
        strPrice = '  $' + str(pricy)
        window['price'].update(strPrice)

        shipType = pickFormat(findZone(zipCode), UIvalues['-COMBO-'], UIvalues['-CHECKBOX1-'], zipCode)
        window['shippingType'].update(shipType)
        print(letterList)
        print(findZone(zipCode))
        subprocess.check_call('echo '+strPrice.strip()+'|clip', shell=True)

window.close()
