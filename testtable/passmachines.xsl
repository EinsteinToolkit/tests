<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/machines">
    <html>
      <head>
        <title>Failing tests</title>
        <link href="testtable.css" rel="stylesheet" type="text/css"/>
        <link rel="stylesheet" type="text/css" href="/static/07430726/css/style.css" />
        <link rel="stylesheet" type="text/css" href="/static/07430726/css/color.css" />
        <base target="_parent"/>

        <style>
          .vertical-text {
          display: inline-block;
          overflow: hidden;
          width: 1.5em;
          }
          .vertical-text__inner {
          display: inline-block;
          white-space: nowrap;
          line-height: 1.5;
          transform: translate(0,100%) rotate(-90deg);
          transform-origin: 0 0;
          -webkit-transform: translate(0,100%) rotate(-90deg);
          -webkit-transform-origin: 0 0;
          }
          /* This element stretches the parent to be square
          by using the mechanics of vertical margins  */
          .vertical-text__inner:after {
          content: "";
          display: block;
          margin: -1.5em 0 100%;
          }


        </style>


      </head>
      <body>
        <table class="pane">
          <tr>
            <td class="pane-header">Machine</td>
          </tr>
          <xsl:for-each select="machine">
            <tr>
              <td class="pane"><xsl:value-of select="@name"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
