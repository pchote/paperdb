var targetData = [];

function buildlinks(value, row, index) {
  links = [];
  if (row['ads'])
    links.push('<a href="' + row['ads'] + '" target="_blank">ADS</a>');

  if (row['doi'])
    links.push('<a href="' + row['doi'] + '" target="_blank">DOI</a>');

  if (row['arxiv'])
    links.push('<a href="' + row['arxiv'] + '" target="_blank">arXiv</a>');

  if (row['url'])
    links.push('<a href="' + row['url'] + '" target="_blank">Web</a>');

  if (row['pdf'])
    links.push('<a href="' + row['pdf'] + '" target="_blank">PDF</a>');

  return links.join('<br />');
}

function multiline(value, row, index) {
  if (value instanceof Array)
    return value.join('<br />');
  return value;
}

function setup() {
  $('#table').bootstrapTable({columns: [
    {field: 'author', title: 'Author', formatter: multiline, sortable: true},
    {field: 'year', title: 'Year', sortable: true},
    {field: 'journal', title: 'Journal', sortable: true},
    {field: 'title', title: 'Title'},
    {field: 'keywords', title: 'Keywords', formatter: multiline},
    {field: '', title: 'Links', formatter: buildlinks}
  ]});
  $.ajax ({
    url: generateURL,
    type: "GET",
    success: function(data){
      $('#table').bootstrapTable("load", data);
    },
    statusCode: {
      500: function() { $('#error').html('Failed to query papers'); }
    }
  });
}
