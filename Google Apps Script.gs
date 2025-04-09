function BoldAndCleanText_Corrected() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  const regex = /#####([\s\S]*?)#####/g;

  for (let row = 0; row < values.length; row++) {
    for (let col = 0; col < values[row].length; col++) {
      let cellText = values[row][col];

      // Only process strings
      if (typeof cellText === 'string') {
        const originalText = cellText;
        const matches = [...originalText.matchAll(regex)];

        // Skip if no matches
        if (matches.length === 0) continue;

        let cleanText = '';
        let boldRanges = [];
        let cursor = 0;

        // Build cleaned text and record bold positions
        for (const match of matches) {
          const start = match.index;
          const end = start + match[0].length;
          const boldText = match[1];

          // Add normal text before the match
          if (cursor < start) {
            cleanText += originalText.substring(cursor, start);
          }

          // Add the bold text (without hashes)
          const boldStart = cleanText.length;
          cleanText += boldText;
          boldRanges.push({ start: boldStart, length: boldText.length });

          cursor = end;
        }

        // Add any text after the last match
        if (cursor < originalText.length) {
          cleanText += originalText.substring(cursor);
        }

        // Apply rich text with bold formatting
        const builder = SpreadsheetApp.newRichTextValue().setText(cleanText);
        const boldStyle = SpreadsheetApp.newTextStyle().setBold(true).build();

        for (const range of boldRanges) {
          builder.setTextStyle(range.start, range.start + range.length, boldStyle);
        }

        range.getCell(row + 1, col + 1).setRichTextValue(builder.build());
      }
    }
  }

  SpreadsheetApp.getUi().alert('Formatting Complete!');
}
