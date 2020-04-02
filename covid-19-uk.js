function drawChart(indicator, cutoff) {

    const width = 800;
    const height = 600;
    const margin = ({top: 40, right: 45, bottom: 30, left: 45})

    // const indicator = "Deaths"
    // const cutoff = 10;
    // const indicator = "ConfirmedCases"
    // const cutoff = 100;

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
        const indictorData = data.filter(d => d.indicator === indicator);
        
        const grouped = d3.groups(indictorData, d => d.country)
            // .map(d => { dailyValues(d[1]); return d })
            // .map(d => { d[1].forEach(e => e.value = e.dailyValue); return d })
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
        svg.append("text")
            .attr("x", margin.left)
            .attr("y", 24)
            .text(`UK COVID-19 cumulative ${indicatorLower}, by number of days since ${cutoff}th ${indicatorLowerSingular}`)
            .attr("font-family", "sans-serif")
            .attr("font-size", "16px");
        
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

function dailyValues(arr) {
    arr.forEach((elt, i, a) => elt.dailyValue = i == 0 ? null : elt.value - a[i - 1].value);
    return arr;
}