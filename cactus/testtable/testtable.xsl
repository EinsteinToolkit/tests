<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/tests">
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
        <!-- <h1>Failing tests</h1> -->
        <table class="pane">

          <tr>
            <td colspan="2" class="pane-header" style="text-align: left">Machine</td>
            <xsl:for-each select="machine">
              <td class="pane-header">
                <div class="vertical-text"><div class="vertical-text__inner" style="text-align: left">
                <xsl:value-of select="text()"/>
                  </div>
                </div>
              </td>
              </xsl:for-each>
          </tr>

          <tr>
            <td colspan="2" class="pane-header" style="text-align: left">Version</td>
            <xsl:for-each select="machine">
              <td class="pane-header" title="{@rev_log}">
                <xsl:value-of select="@rev_seqno"/>
              </td>
              </xsl:for-each>
          </tr>

          <tr>
            <td colspan="2" class="pane-header">Failures</td>
            <xsl:for-each select="machine">
              <td class="pane-header">
                <xsl:value-of select="@num_failures"/>/<xsl:value-of select="@num_tests"/>
              </td>
              </xsl:for-each>
          </tr>

          <tr>
            <td class="pane-header">Class</td>
            <td class="pane-header">Test</td>
            <xsl:for-each select="machine">
              <td class="pane-header">
              </td>
              </xsl:for-each>
          </tr>

          <xsl:for-each select="test">
            <tr>
              <td class="pane"><xsl:value-of select="classname"/></td>
              <td class="pane"><xsl:value-of select="name"/></td>
              <xsl:for-each select="machine">
                <td class="pane" style="text-align: center;">
                <a class="lowkey" href="{state/@link}"><xsl:value-of select="state"/></a></td>
              </xsl:for-each>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
