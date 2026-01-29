<!-- Source: Labelary API Documentation -->
<!-- Section: Web and Scripting Examples -->
<!-- Generated: 2025-11-02 19:43:59 -->

# 5. Examples

The code snippets and examples below are intended to help you start consuming the Labelary API quickly, regardless of your client-side technology stack.

## 5.1. Live Examples

Some live examples that use GET requests to convert the ZPL encoded in the URLs into PNG images:

- http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/^xa^cfa,50^fo100,100^fdHello World^fs^xz
- http://api.labelary.com/v1/printers/12dpmm/labels/3.5x1.5/0/^xa^cfa,50^fo100,100^fdSmaller Label^fs^xz
- http://api.labelary.com/v1/printers/6dpmm/labels/4x6/1/^xa^cfa,50^fo100,100^fdFirst Label^fs^xz^xa^cfa,50^fo100,100^fdSecond Label^fs^xz

## 5.2. curl Examples

**Using the GET method:**
```bash
curl --get http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data-urlencode "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

**Using the POST method (with application/x-www-form-urlencoded content):**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --data "^xa^cfa,50^fo100,100^fdHello World^fs^xz" > label.png
```

**Using the POST method (with multipart/form-data content):**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --form file=@label.zpl > label.png
```

**Using the POST method (with multipart/form-data content), requesting a PDF file instead of a PNG image:**
```bash
curl --request POST http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ \
  --form file=@label.zpl \
  --header "Accept: application/pdf" > label.pdf
```

## 5.3. Postman Examples

You can also test the Labelary API by importing this request collection into Postman and running any of the requests therein.

## 5.4. PowerShell Examples

**Using the POST method to request a PNG image:**
```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ `
  -ContentType "application/x-www-form-urlencoded" `
  -InFile label.zpl `
  -OutFile label.png
```

**Using the POST method to request a PDF file:**
```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/ `
  -ContentType "application/x-www-form-urlencoded" `
  -Headers @{"Accept" = "application/pdf"} `
  -InFile label.zpl `
  -OutFile label.pdf
```

## 5.5. ColdFusion Example

A ColdFusion example that uses a POST request to convert a ZPL string to a PDF file:

```coldfusion
<cfoutput>
    <cfset zpl="^xa^cfa,50^fo100,100^fdHello World^fs^xz">
    <!-- change type to "image/png" to get PNG images -->
    <cfset type="application/pdf">
    <!-- adjust print density, label width, label height, and label index as necessary -->
    <cfhttp url="http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/" method="post" result="result">
        <cfhttpparam type="header" name="Content-Type" value="application/x-www-form-urlencoded">
        <cfhttpparam type="header" name="Accept" value="#type#">
        <cfhttpparam type="body" value="#zpl#">
    </cfhttp>
    <cfcontent variable="#result.Filecontent#" type="#type#" reset="true" />
</cfoutput>
```

## 5.6. PHP Example

A PHP example that uses a POST request to convert a ZPL string to a PDF file:

```php
<?php

$zpl = "^xa^cfa,50^fo100,100^fdHello World^fs^xz";

$curl = curl_init();
// adjust print density, label width, label height, and label index as necessary
curl_setopt($curl, CURLOPT_URL, "http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/");
curl_setopt($curl, CURLOPT_POST, TRUE);
curl_setopt($curl, CURLOPT_POSTFIELDS, $zpl);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, TRUE);
curl_setopt($curl, CURLOPT_HTTPHEADER, array("Accept: application/pdf")); // omit this line to get PNG images back
$result = curl_exec($curl);

if (curl_getinfo($curl, CURLINFO_HTTP_CODE) == 200) {
    $file = fopen("label.pdf", "w"); // change file name for PNG images
    fwrite($file, $result);
    fclose($file);
} else {
    print_r("Error: $result");
}

curl_close($curl);

?>
```

## 5.7. Excel VBA Example

An Excel VBA example that converts all ZPL templates in column A into PNG label images, and adds the images to column B:

```vba
Sub Convert()

    'adjust print density, label width, label height, and label index as necessary
    u = "http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/"
    tempFile = Environ("Temp") & "\excel-label-temp.png"
    Set ws = ActiveWorkbook.Sheets("Sheet1")
    Set http = CreateObject("MSXML2.ServerXMLHTTP")
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 1 'adTypeBinary

    For Each rw In ws.UsedRange.Rows
        zpl = ws.Cells(rw.Row, 1).Value
        http.Open "POST", u, False
        http.SetRequestHeader "Content-Type", "application/x-www-form-urlencoded"
        http.Send zpl
        If http.Status = 200 Then
            stream.Open
            stream.Write http.responseBody
            stream.SaveToFile tempFile, 2 'adSaveCreateOverWrite
            stream.Close
            rw.RowHeight = 200
            Set pic = ws.Shapes.AddPicture(tempFile, False, True, 1, 1, 1, 1)
            pic.Left = ws.Cells(rw.Row, 2).Left
            pic.Top = ws.Cells(rw.Row, 2).Top
            pic.Width = ws.Cells(rw.Row, 2).Width
            pic.Height = ws.Cells(rw.Row, 2).Height
        Else
            ws.Cells(rw.Row, 2).Value = http.ResponseText
        End If
    Next rw

End Sub
```