function drawChart(indicator, cutoff, daily) {

    const width = 800;
    const height = 600;
    const margin = ({top: 40, right: 45, bottom: 30, left: 45})

    const parseDate = d3.timeParse("%Y-%m-%d");

    const colours = {
        "England": d3.schemeCategory10[3],
        "Wales": d3.schemeCategory10[2],
        "Scotland": d3.schemeCategory10[0],
        "Northern Ireland": d3.schemeCategory10[9],
        "UK": d3.schemeCategory10[4],
    }

    d3.csv("data/covid-19-indicators-uk.csv", function(d) {
        return {
            date: parseDate(d['Date']),
            country: d['Country'],
            indicator: d['Indicator'],
            value: +d['Value']
        }
    }, function(data) {
        const indicatorData = data.filter(d => d.indicator === indicator)
            //.filter(d => d.country === "UK")

        const indicatorDataGrouped = d3.groups(indicatorData, d => d.country)

        let grouped = indicatorDataGrouped
        if (daily) {
            grouped = indicatorDataGrouped
                // calculate daily values from cumulative values
                .map(d => { dailyValues(d[1]); return d })
                .map(d => { d[1].forEach(e => e.value = e.dailyValue); return d })
                // apply moving average to last 7 days for smoothing
                .map(d => { 
                    d[1] = d3.zip(d[1], movingAverage(d[1], 7)).map(e => { e[0].value = e[1]; return e[0]});
                    return d
                })
        }
        
        grouped = grouped
            // truncate to cutoff
            .map(d => {
                d[1] = truncate(d[1], cutoff)
                return d;
            })

        const x = d3.scaleLinear()
            .domain([
                0,
                d3.max(grouped, d => d[1].length) + 7 // add one week
            ])
            .range([margin.left, width - margin.right])

        const y = d3.scaleLog()
            .domain([cutoff, getNextLogBoundary(d3.max(grouped, d => d3.max(d[1].map(e => e.value))))])
            .range([height - margin.bottom, margin.top])

        const svg = d3.select("#dataviz")
            .append("svg")
            .attr("width", width)
            .attr("height", height);    

        // Gridlines from https://bl.ocks.org/d3noob/c506ac45617cf9ed39337f99f8511218
        function make_x_gridlines() {		
            return d3.axisBottom(x)
                .tickValues(getTickValuesLinear(x.domain(), 5))
        }
        svg.append("g")
            .attr("transform", `translate(0,${height - margin.bottom})`) 
            .call(make_x_gridlines()
                .tickSize(0));
        svg.append("g")			
            .attr("class", "grid")
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(make_x_gridlines()
                .tickSize(-(height - margin.top - margin.bottom))
                .tickFormat("")
            )

        const yTickValues = getTickValuesLog(y.domain())
        function make_y_gridlines() {		
            return d3.axisLeft(y)
                .tickValues(yTickValues)
        }
        svg.append("g")
            .attr("class", "grid")
            .attr("transform", `translate(${width - margin.right},0)`) 
            .call(d3.axisRight(y)
                .tickValues(yTickValues)
                .tickFormat(d3.format(",d"))
                .tickSize(0)
            )
        svg.append("g")			
            .attr("class", "grid")
            .attr("transform", `translate(${margin.left},0)`) 
            .call(make_y_gridlines()
                .tickSize(-(width - margin.left - margin.right))
                .tickFormat(d3.format(",d"))
            )

        // Doubling lines
        if (!daily) {
            const maxX = x.domain()[1];
            svg.append("g")
                .append("clipPath")
                    .attr("id", "rect-clip")
                .append("rect")
                    .attr("x", x(x.domain()[0]))
                    .attr("y", y(y.domain()[1]))
                    .attr("width", x(x.domain()[1]) - x(x.domain()[0]))
                    .attr("height", y(y.domain()[0]) - y(y.domain()[1]))
                    .style("stroke-opacity", 0)
                    .style("fill-opacity", 0);
            svg.append("path")
                .attr("class", "doubling-line")
                .attr("clip-path", "url(#rect-clip)")
                .attr('d', d3.line()([[x(0), y(cutoff)], [x(maxX), y(doubling(cutoff, maxX, 1))]]))
            svg.append("path")
                .attr("class", "doubling-line")
                .attr("clip-path", "url(#rect-clip)")
                .attr('d', d3.line()([[x(0), y(cutoff)], [x(maxX), y(doubling(cutoff, maxX, 2))]]))
            svg.append("path")
                .attr("class", "doubling-line")
                .attr("clip-path", "url(#rect-clip)")
                .attr('d', d3.line()([[x(0), y(cutoff)], [x(maxX), y(doubling(cutoff, maxX, 3))]]))
            svg.append("path")
                .attr("class", "doubling-line")
                .attr("clip-path", "url(#rect-clip)")
                .attr('d', d3.line()([[x(0), y(cutoff)], [x(maxX), y(doubling(cutoff, maxX, 7))]]))

            svg.append("text")
                .attr("class", "doubling-text")
                .text("Doubling every day")
                .attr("x", x(inverseDoubling(cutoff, y.domain()[1], 1)))
                .attr("y", y(y.domain()[1]) + 20)
                .attr("fill", "black")
            svg.append("text")
                .attr("class", "doubling-text")
                .text("2 days")
                .attr("x", x(inverseDoubling(cutoff, y.domain()[1], 2)))
                .attr("y", y(y.domain()[1]) + 20)
                .attr("fill", "black")
            svg.append("text")
                .attr("class", "doubling-text")
                .text("3 days")
                .attr("x", x(inverseDoubling(cutoff, y.domain()[1], 3)))
                .attr("y", y(y.domain()[1]) + 20)
                .attr("fill", "black")
            svg.append("text")
                .attr("class", "doubling-text")
                .text("week")
                .attr("x", x(maxX) - 20)
                .attr("y", y(doubling(cutoff, maxX, 7)) + 20)
                .attr("fill", "black")
        }

        const line = d3.line()
            .x((d, i) => x(i))
            .y(d => y(d.value))

        grouped.forEach(d => {
            svg.append("path")
                .attr("class", "line")
                .attr("stroke", colours[d[0]])
                .attr("d", line(d[1]));
            const last = d[1][d[1].length - 1];
            svg.append("circle")
                .attr("class", "circle")
                .attr("r", 4)
                .attr("cx", x(d[1].length - 1))
                .attr("cy", y(last.value))
                .attr("fill", colours[d[0]])

        })

        // Add text on top
        grouped.forEach(d => {
            const last = d[1][d[1].length - 1];
            svg.append("text")
                .attr("class", "text-shadow")
                .text(d[0])
                .attr("x", x(d[1].length - 1) + 10)
                .attr("y", y(last.value) + 2)
                .attr("fill", colours[d[0]])
            svg.append("text")
                .attr("class", "text")
                .text(d[0])
                .attr("x", x(d[1].length - 1) + 10)
                .attr("y", y(last.value) + 2)
                .attr("fill", colours[d[0]])
        })

        const indicatorLower = indicator.replace(/([A-Z])/g, " $1").toLowerCase()
        const indicatorLowerSingular = indicatorLower.substr(0, indicatorLower.length - 1)
        if (daily) {
            svg.append("text")
                .attr("x", margin.left)
                .attr("y", 24)
                .text(`UK COVID-19 daily ${indicatorLower} (7 day rolling average), by number of days since ${ordinalSuffix(cutoff)} ${indicatorLowerSingular}`)
                .attr("font-family", "sans-serif")
                .attr("font-size", "16px");
        } else {
            svg.append("text")
                .attr("x", margin.left)
                .attr("y", 24)
                .text(`UK COVID-19 cumulative ${indicatorLower}, by number of days since ${ordinalSuffix(cutoff)} ${indicatorLowerSingular}`)
                .attr("font-family", "sans-serif")
                .attr("font-size", "16px");
        }
        
    });

}

// Truncate an array dropping initial elements that have a value less than a cutoff.
function truncate(arr, cutoff) {
    const firstIndex = arr.findIndex(d => d.value >= cutoff);
    if (firstIndex == -1) {
        return [];
    } else {
        return arr.slice(firstIndex);
    }
}

function getNextLogBoundary(y) {
    const log2 = Math.log10(2)
    const log5 = Math.log10(5)
    const fracLogY = Math.log10(y) % 1; // the fractional part of the log of y
    // add one to each to avoid rounding errors that would mean the value wasn't rendered
    if (fracLogY < log2) {
        return Math.pow(10, Math.floor(Math.log10(y)) + log2) + 1
    } else if (fracLogY < log5) {
        return Math.pow(10, Math.floor(Math.log10(y)) + log5) + 1
    } else {
        return Math.pow(10, Math.floor(Math.log10(y)) + 1) + 1
    }
}

function getTickValuesLinear(domain, interval) {
    return d3.range(domain[0], domain[1], interval)
}

function getTickValuesLog(domain) {
    const tickValues = []
    let e = 0
    outer: while (true) {
        for (v of [1, 2, 5]) {
            let tick = v * Math.pow(10, e)
            if (tick > domain[1]) {
                break outer
            } else if (tick >= domain[0]) {
                tickValues.push(tick);
            }
        }
        e++;
    }
    return tickValues
}

function movingAverage(arr, windowSize) {
    const result = []
    for (let i = 1; i <= arr.length; i++) {
        const sub = arr.slice(Math.max(0, i - windowSize), i)
        result.push(d3.mean(sub, d => d.value))
    }
    return result;
}

function dailyValues(arr) {
    arr.forEach((elt, i, a) => elt.dailyValue = i == 0 ? null : elt.value - a[i - 1].value);
    return arr;
}

function doubling(cutoff, dayNumber, numberOfDaysToDouble) {
    return cutoff * Math.pow(2, dayNumber / numberOfDaysToDouble)
}

function inverseDoubling(cutoff, value, numberOfDaysToDouble) {
    const dayNumber = numberOfDaysToDouble * Math.log2(value / cutoff);
    return dayNumber
}

function ordinalSuffix(i) {
    var j = i % 10,
        k = i % 100;
    if (j == 1 && k != 11) {
        return i + "st";
    }
    if (j == 2 && k != 12) {
        return i + "nd";
    }
    if (j == 3 && k != 13) {
        return i + "rd";
    }
    return i + "th";
}