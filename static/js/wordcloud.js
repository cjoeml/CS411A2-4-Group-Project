var d3 = require("d3"),
    cloud = require("d3-cloud");

var fill = d3.scale.category20();

var normalization_value = largest_occurence / number_of_words;

var layout = cloud()
    .size([750,500])
    .words(words_in_tweets.map(function(d) {
      return {text: d, size: 20 + ((word_frequency[d] /  number_of_words) / normalization_value) * 90};
    }))
    .padding(5)
    .rotate(function() { return ~~(Math.random() * 2) * 90; })
    .font("Impact")
    .fontSize(function(d) { return d.size; })
    .on("end", draw);

layout.start();

function draw(words) {
  console.log(number_of_words);
  d3.select(".wordcloud-container").append("svg")
      .attr("width", layout.size()[0])
      .attr("height", layout.size()[1])
    .append("g")
      .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
    .selectAll("text")
      .data(words)
    .enter().append("text")
      .style("font-size", function(d) { return d.size + "px"; })
      .style("font-family", "Impact")
      .style("fill", function(d, i) { return fill(i); })
      .attr("text-anchor", "middle")
      .attr("transform", function(d) {
        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
      })
      .text(function(d) { return d.text; });
}