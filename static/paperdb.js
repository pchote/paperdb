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

function buildnames(value, row, index) {
  if (value instanceof Array)
    return '<span data-tooltip="true" data-placement="bottom" title="' + value.join('<br />') + '">' + value[0] + (value.length > 1 ? ' et al' : '') + '</span>';
  return value;
}

function buildtitle(value, row, index) {
  return '<span data-tooltip="true" data-placement="bottom" title="' + row['abstract'] + '">' + value + '</span>';
}

function buildjournal(value, row, index) {
  if (row['keywords'])
    return '<span data-tooltip="true" data-placement="bottom" title="' + row['keywords'].split(",").join("<br />") + '">' + value + '</span>';
  return value;
}

function multiline(value, row, index) {
  if (value instanceof Array)
    return value.join('<br />');
  return value;
}

$(function() {
  $('#table').on('post-body.bs.table', function() {
    $('[data-tooltip="true"]').tooltip({
      container: "body",
      html: true,
    });
  });

  $('#table').on('load-error.bs.table', function() {
    $('#table').bootstrapTable('updateFormatText', 'NoMatches', 'There are no papers to display. Have you logged in?');
  });
});
