import React, {useContext, useEffect, useRef, useState} from "react";
import {AppContext, domain, mode} from "../../App";
import {
    scaleLinear,
    scaleTime,
    scaleOrdinal
} from 'd3-scale';
import {drag} from 'd3-drag';

import { select, selectAll } from 'd3-selection';
import {zoom, zoomTransform} from "d3-zoom";
import {forceCenter, forceLink, forceManyBody, forceSimulation} from "d3-force";
import {schemeCategory10} from "d3-scale-chromatic";

import './graph.css'


function  D3Graph({report_id, language}) {
    let reportID = report_id;
    let d3svgchartID = "D3-chart";
    let d3svgchartgID = "D3-chart-g";
    const url_report_JSON = domain+"report_json/"+reportID+"/"+language;
    const url_report_JSON_development = "http://localhost:4000/report_json";
    // const {d3Graph} = useContext(AppContext)
    // const [graph, setGraph] = d3Graph;
    const svgRef = useRef();
    const svgGRef = useRef();
    // const {fullScreenLoading} = useContext(AppContext);
    const [LoadingFullScreen, SetLoadingFullScreen] = useState(false);


    function drawChart(){

        const svg = select("#"+d3svgchartID);


        // var defs = svg.append("defs");

// Add the path using this helper function
        svg.append('circle')
            .attr('cx', 100)
            .attr('cy', 100)
            .attr('r', 50)
            .attr('stroke', 'black')
            .attr('fill', '#69a3b2');


    }

    function D3createGraph(report)
    {

        console.dir(report);

        let graph = {nodes: [], links: []};
        let colors = {'pink':'#FFBFBF', 'orange': '#FF9300', 'blue':'#0096FF', 'light_green': '#BFFFBF'};

        let centre_node = {};

        for (let property in report)
        {
            console.log(property+" "+report[property]);
            if(property == "ReportID")
            {
                let id_report = report[property];
                centre_node["id"]="id_report";
                centre_node["property"]="id_report";
                centre_node["value"]=id_report;
                //centre_node["label_node"]=id_report.replace("https://w3id.org/examode/resource/","...");
                let ClinicalCase = report["ClinicalCase"];
                let ClinicalCase_desc = report["entities"]["ClinicalCase"]["desc"];

                centre_node["label_node"] = ClinicalCase_desc;
                centre_node["color"] = colors["light_green"];
                centre_node["size"] = 20;
                graph["nodes"].push(centre_node);


            }
            else if(property == "patient")
            {

                let patient_identifier_label = report["patient"]["PatientURL"].replace("https://w3id.org/examode/resource/patient/","")
                let node_patient = {"id":"patient", "value":report["patient"]["PatientURL"], "ontology-link": report["patient"]["a"], "label_node": "Patient: "+patient_identifier_label, "size":20, "color":colors["light_green"] };
                let link_patient_report = {"source": "id_report", "target":"patient", "type":"patient-report-link", "value": 1, "label":"exa:hasClinicalCaseReport", "target-size":0};
                graph["links"].push(link_patient_report);
                graph["nodes"].push(node_patient);

                // hasGenderLiteral
                if (report["patient"].hasOwnProperty("hasGenderLiteral")) {
                    let gender = report["patient"]["hasGenderLiteral"];
                    let node_hasGenderLiteral = {
                        "id": "hasGenderLiteral",
                        "value": gender,
                        "ontology-link": report["patient"]["hasGender"],
                        "label_node": gender,
                        "size": 0,
                        "color": colors["light_green"]
                    };
                    let link_hasGenderLiteral_patient = {
                        "source": "patient",
                        "target": "hasGenderLiteral",
                        "type": "hasGenderLiteral-patient-link",
                        "value": 1,
                        "label": "exa:hasGender",
                        "target-size": 0
                    };
                    graph["links"].push(link_hasGenderLiteral_patient);
                    graph["nodes"].push(node_hasGenderLiteral);
                }


                // hasAge
                if (report["patient"].hasOwnProperty("hasAge"))
                {
                    let node_hasAge = {"id":"hasAge", "value":report["patient"]["hasAge"], "label_node":report["patient"]["hasAge"], "size":0};
                    let link_hasAge_patient = {"source":"patient", "target":"hasAge", "type": "hasAge-patient-link", "value": 1, "label":"exa:hasAge", "target-size":0};
                    graph["links"].push(link_hasAge_patient);
                    graph["nodes"].push(node_hasAge);
                }

                // hasAgeOnset
                if (report["patient"].hasOwnProperty("hasAgeOnset")) {
                    let hasAgeOnset_literal = "";
                    if (report["patient"]["hasAgeOnset"] != null && report["patient"]["hasAgeOnset"].includes("HP:0011462")) {
                        hasAgeOnset_literal = "Young adult onset "
                    } else if (report["patient"]["hasAgeOnset"] != null && report["patient"]["hasAgeOnset"].includes("HP:0003596")) {
                        hasAgeOnset_literal = "Middle age onset"
                    } else if (report["patient"]["hasAgeOnset"] != null && report["patient"]["hasAgeOnset"].includes("HP:0003584")) {
                        hasAgeOnset_literal = "Late onset"
                    }
                    if (hasAgeOnset_literal != "") {
                        let node_hasAgeOnset = {
                            "id": "hasAgeOnset",
                            "value": report["patient"]["hasAgeOnset"],
                            "ontology-link": report["patient"]["hasAgeOnset"],
                            "label_node": hasAgeOnset_literal,
                            "size": 0
                        };
                        let link_hasAgeOnset_patient = {
                            "source": "patient",
                            "target": "hasAgeOnset",
                            "type": "hasAge-patient-link",
                            "value": 1,
                            "label": "exa:ageOnset",
                            "target-size": 0
                        };
                        graph["links"].push(link_hasAgeOnset_patient);
                        graph["nodes"].push(node_hasAgeOnset);
                    }

                }




            }
            else if(property == "slides")
            {

                let slides = report[property];
                for (const [slide_index, slide_i] of slides.entries()) {
                    console.log(slide_i);
                    let hasSlideId = slide_i["hasSlideId"];
                    let node_slide_i = {"id":"hasSlide_"+hasSlideId, "property": "Slide", "value": 1, "color":colors["light_green"], "label_node": "Slide", "size":20 }
                    let node_hasSlideId = {"id":"hasSlideId_"+hasSlideId, "property": "hasSlideId", "value": 1, "color":colors["light_green"], "label_node": hasSlideId, "size":0 }
                    graph["nodes"].push(node_hasSlideId);
                    graph["nodes"].push(node_slide_i);
                    let link_slide_hasSlideId = {"source": "hasSlide_"+hasSlideId, "target":"hasSlideId_"+hasSlideId, "type":"slide-hasSlideId", "value": 1, "label":"exa:hasSlideId", "target-size":0};
                    let link_slide_report = {"source": "id_report", "target":"hasSlide_"+hasSlideId, "type":"report-slide", "value": 1, "label":"exa:hasSlide", "target-size": 20};
                    graph["links"].push(link_slide_hasSlideId);
                    graph["links"].push(link_slide_report);
                }


            }

            // else if(property == "hasGender" || property == "clinical_case" || property == "url_report" || property == "hasAge" || property == "entities")
            else if(property == "entities")
            {
                // Do nothing
            }
            else if(property == "hasOutcome")
            {
                let outcomes = report[property];
                for (const [i, outcome] of outcomes.entries())
                {
                    //console.log(outcome);
                    let id_outcome = outcome["OutcomeURL"];
                    let outcome_index = null;
                    for (const [j, outcome_j] of report["entities"][property].entries())
                    {
                        if (outcome_j["iri"] == outcome["OutcomeURL"])
                        {
                            outcome_index = j;
                            break;
                        }
                    }
                    let outcome_a = outcome["a"];
                    let outcome_a_desc = report["entities"]["hasOutcome"][outcome_index]["a"]["desc"];

                    // hasDysplasia
                    let hasDysplasia = null;
                    if (outcome.hasOwnProperty("hasDysplasia")) {
                        hasDysplasia = outcome["hasDysplasia"];
                    }
                    // hasLocation
                    let hasLocation = null;
                    if (outcome.hasOwnProperty("hasLocation")) {
                        hasLocation = outcome["hasLocation"];
                    }
                    // hasIntervention
                    let hasIntervention = null;
                    if (outcome.hasOwnProperty("hasIntervention")) {
                        hasIntervention = outcome["hasIntervention"];
                    }

                    // detectedHumanPapillomaVirus
                    let detectedHumanPapillomaVirus = null;
                    if (outcome.hasOwnProperty("detectedHumanPapillomaVirus")) {
                        detectedHumanPapillomaVirus = outcome["detectedHumanPapillomaVirus"];
                        let detectedHumanPapillomaVirus_desc = report["entities"]["hasOutcome"][outcome_index]["detectedHumanPapillomaVirus"]["desc"];
                        let node_detectedHumanPapillomaVirus = {"id":"detectedHumanPapillomaVirus_"+i, "property": "detectedHumanPapillomaVirus", "value":detectedHumanPapillomaVirus_desc, "color":colors["blue"], "label_node": detectedHumanPapillomaVirus_desc, "size":20 }
                        graph["nodes"].push(node_detectedHumanPapillomaVirus);
                        let link_outcome_detectedHumanPapillomaVirus_i = {"source":"outcome_"+i, "target":"detectedHumanPapillomaVirus_"+i, "type":"outcome-detectedHumanPapillomaVirus-link", "label":"exa:detectedHumanPapillomaVirus", "target-size":20};
                        graph["links"].push(link_outcome_detectedHumanPapillomaVirus_i);
                    }

                    console.log(hasIntervention);

                    let node_outcome = {"id":"outcome_"+i, "property": "outcome", "value":id_outcome, "hasDysplasia": hasDysplasia, "interventions": hasIntervention, "color":colors["blue"], "label_node": id_outcome.replace("https://w3id.org/examode/resource/","..."), "size":20  }
                    graph["nodes"].push(node_outcome);

                    if(outcome_a != undefined && outcome_a != "")
                    {
                        let node_type = {"id":"outcomeType_"+i, "property": "outcomeType", "value":outcome_a_desc, "color":colors["blue"], "label_node": outcome_a_desc, "size":0 }
                        graph["nodes"].push(node_type);
                        let link_outcome_dysplasia = {"source":"outcome_"+i, "target":"outcomeType_"+i, "type":"outcome-type-link", "label":"a", "target-size":0};
                        graph["links"].push(link_outcome_dysplasia);
                    }




                    if(hasDysplasia!= undefined && hasDysplasia != [])
                    {
                        for (const [dysplasia_index, hasDysplasia_i] of hasDysplasia.entries())
                        {
                            // let hasDysplasia_ii = hasDysplasia_i
                            // if(hasDysplasia_i.includes("MONDO_0002271"))
                            // {
                            //     hasDysplasia_ii = "Colon Adenocarcinoma";
                            // }
                            // else if(hasDysplasia_i.includes("SevereColonDysplasia"))
                            // {
                            //     hasDysplasia_ii = "Severe Colon Dysplasia";
                            // }
                            // else if(hasDysplasia_i.includes("NCIT_C4847"))
                            // {
                            //     hasDysplasia_ii = "Colon Dysplasia";
                            // }
                            // else if(hasDysplasia_i.includes("NCIT_C4848"))
                            // {
                            //     hasDysplasia_ii = "Mild Colon Dysplasia";
                            // }
                            // else if(hasDysplasia_i.includes("NCIT_C4849"))
                            // {
                            //     hasDysplasia_ii = "Moderate Colon Dysplasia";
                            // }
                            // else if(hasDysplasia_i.includes("NCIT_C8362"))
                            // {
                            //     hasDysplasia_ii = "Mild Dysplasia";
                            // }
                            // else if(hasDysplasia_i.includes("NCIT_C8363"))
                            // {
                            //     hasDysplasia_ii = "Moderate Dysplasia";
                            // }
                            // else if(hasDysplasia_i.includes("NCIT_C156083"))
                            // {
                            //     hasDysplasia_ii = "High Grade Dysplasia";
                            // }
                            // else if(hasDysplasia_i.includes("NCIT_C4849"))
                            // {
                            //     hasDysplasia_ii = "Severe Dysplasia";
                            // }
                            // else if(hasDysplasia_i.includes("PreCancerousDysplasia"))
                            // {
                            //     hasDysplasia_ii = "Pre-Cancerous Dysplasia, Susp. For Malignancy";
                            // }

                            let hasDysplasia_i_desc = report["entities"]["hasOutcome"][outcome_index]["hasDysplasia"][dysplasia_index]["desc"];

                            let node_dysplasia_i = {"id":"hasDysplasia_"+i+"_"+dysplasia_index, "property": "hasDysplasia", "value":hasDysplasia_i_desc, "color":colors["blue"], "label_node": hasDysplasia_i_desc, "size":20 }
                            graph["nodes"].push(node_dysplasia_i);
                            let link_outcome_dysplasia_i = {"source":"outcome_"+i, "target":"hasDysplasia_"+i+"_"+dysplasia_index, "type":"outcome-hasDysplasia-link", "label":"exa:hasDysplasia", "target-size":20};
                            graph["links"].push(link_outcome_dysplasia_i);
                        }

                    }
                    if(hasLocation!= undefined && hasLocation != "")
                    {
                        for (const [location_index, hasLocation_i] of hasLocation.entries()) {

                            let hasLocation_i_desc = report["entities"]["hasOutcome"][outcome_index]["hasLocation"][location_index]["desc"];
                            let node_location = {
                                "id": "hasLocation_" + i +"_"+location_index,
                                "property": "hasLocation",
                                "color": colors["blue"],
                                "value": hasLocation_i_desc,
                                "label_node": hasLocation_i_desc,
                                "size": 20
                            }
                            graph["nodes"].push(node_location);
                            let link_outcome_location = {
                                "source": "outcome_" + i,
                                "target": "hasLocation_" + i +"_"+location_index,
                                "type": "outcome-hasLocation-link",
                                "label": "exa:hasLocation",
                                "target-size": 20
                            };
                            graph["links"].push(link_outcome_location);
                        }
                    }

                    let link_outcome_report = {"source":"id_report", "target":"outcome_"+i, "type":"outcome-report-link", "value": 1, "label":"exa:hasOutcome", "target-size":20};
                    graph["links"].push(link_outcome_report);

                    if(hasIntervention != undefined)
                    {
                        hasIntervention.forEach(function(intervention, j)
                        {
                            console.log(intervention);
                            let id_intervention = intervention["InterventionURL"];
                            let hasTopography = intervention["hasTopography"];
                            let intervention_a = intervention["a"];
                            let intervention_a_desc = report["entities"]["hasOutcome"][outcome_index]["hasIntervention"][j]["a"]["desc"];

                            console.dir(report["entities"]["hasOutcome"][outcome_index]["hasIntervention"]);
                            console.log(intervention_a_desc);




                            let node_intervention = {"id":"intervention_"+id_outcome+"_"+j, "property": "intervention", "value":id_intervention, "hasTopography": hasTopography, "color":colors["orange"], "label_node": id_intervention.replace("https://w3id.org/examode/resource/","..."), "size": 20 };
                            graph["nodes"].push(node_intervention);

                            if(hasTopography != undefined && hasTopography != "")
                            {
                                for (const [topography_index, hasTopography_i] of hasTopography.entries()) {

                                     console.dir(report["entities"]["hasOutcome"][outcome_index]["hasIntervention"][j]["hasTopography"]);
                                     console.dir(report["entities"]["hasOutcome"][outcome_index]["hasIntervention"][j]);
                                    if (report["entities"]["hasOutcome"][outcome_index]["hasIntervention"][j].hasOwnProperty("hasTopography"))
                                    {
                                        let hasTopography_i_a_desc = report["entities"]["hasOutcome"][outcome_index]["hasIntervention"][j]["hasTopography"][topography_index]["desc"];
                                        let node_topography = {"id":"hasTopography_"+id_intervention+"_"+j+"_"+topography_index, "property": "hasTopography", "value":hasTopography_i_a_desc, "color":colors["orange"], "label_node": hasTopography_i_a_desc, "size":20 };
                                        graph["nodes"].push(node_topography);
                                        let link_intervention_topography = {"source":"intervention_"+id_outcome+"_"+j, "target":"hasTopography_"+id_intervention+"_"+j+"_"+topography_index, "type":"intervention-hasTopography-link", "label":"exa:hasTopography", "target-size":20};
                                        graph["links"].push(link_intervention_topography);
                                    }
                                }
                            }
                            if(intervention_a_desc != undefined && intervention_a_desc != "")
                            {
                                console.log("entered in line 345!!!!!");
                                let node_intervention_type = {"id":"interventionType_"+id_intervention+"_"+j, "property": "interventionType", "value":intervention_a_desc, "color":colors["orange"], "label_node": intervention_a_desc, "size":20 };
                                graph["nodes"].push(node_intervention_type);
                                let link_intervention_type= {"source":"intervention_"+id_outcome+"_"+j, "target":"interventionType_"+id_intervention+"_"+j, "type":"intervention-interventionType-link", "label":"a", "target-size":20};
                                graph["links"].push(link_intervention_type);
                            }

                            let link_outcome_intervention = {"source":"outcome_"+i, "target":"intervention_"+id_outcome+"_"+j, "type":"outcome-intervention-link", "value": 1, "label":"exa:hasIntervention", "target-size":20};
                            graph["links"].push(link_outcome_intervention);
                        });
                    }


                }

            }
            else
            {
                let label_node = "";
                if(typeof report[property] == "string" && report[property].includes("examode/resource"))
                {
                    label_node = report[property].replace("https://w3id.org/examode/resource/","...");
                }
                else
                {
                    label_node = report[property];
                }

                let node = {"id":property, "value":report[property], "label_node": label_node, "size":0 };
                let label = "exa:"+property;

                if(property == "filename")
                {
                    label = "exa:hasImage";
                }


                let link_property_report = {"source":"id_report", "target":property, "type":property+"-report-link", "value": 1, "label":label, "target-size":0};
                graph["links"].push(link_property_report);
                graph["nodes"].push(node);

            }

        }

        return graph;
    }

    function D3_draw_chart(graph) {

        // const document_width = $(document).width();

        //$('#D3-chart-div').width(document_width);
        console.table(graph);

        // console.log(`entered in D3_draw_chart ${svgRef.current.id}`);

        var svg = select(svgRef.current),
             width = +svg.attr("width"),
             height = +svg.attr("height");

        svg.on("mousedown", function(){
            console.log("mouse down");
            svg.style("cursor","move");
        });

        // $('svg').mousedown(function () {
        //     $(this).css("cursor","move");
        // });

        // // Add the path using this helper function
        // svg.append('circle')
        //     .attr('cx', 100)
        //     .attr('cy', 100)
        //     .attr('r', 50)
        //     .attr('stroke', 'black')
        //     .attr('fill', '#69a3b2');


        // let container = d3.select(svgGRef.current);
        let container = null;
        let offsetLeft = null;
        let offsetTop = null;
        let offsetHeight = null;
        let offsetWidth = null;

        let d3DiagElems = selectAll('.MuiDialog-paperScrollPaper');
        if("_groups" in d3DiagElems && d3DiagElems["_groups"].length > 0){
            // If the dialog is shown adapt the graph accordingly
            console.table(d3DiagElems);
            console.dir(d3DiagElems);
            console.dir(d3DiagElems["_groups"]);
            let d3DiagElem = d3DiagElems["_groups"][0][0];
            offsetLeft = d3DiagElem.offsetLeft;
            offsetTop = d3DiagElem.offsetTop;
            offsetHeight = d3DiagElem.offsetHeight;
            offsetWidth = d3DiagElem.offsetWidth;
            console.dir(d3DiagElem);
            console.log(`offsetLeft: ${offsetLeft}, offsetTop:${offsetTop}, offsetHeight:${offsetHeight}, offsetWidth:${offsetWidth}`);

            container = svg.append("g").attr("transform", `translate(${offsetLeft+offsetWidth/2-0.3*(offsetLeft+offsetWidth/2)},${offsetTop+offsetHeight/2-0.2*(offsetTop+offsetHeight/2)}) scale(1)`);
            //container.call(d3.zoom.transform, `translate(${offsetLeft+offsetWidth/2},${offsetTop+offsetHeight/2})`);

            // container.attr('transform',`translate(${offsetLeft+offsetWidth/2},${offsetTop+offsetHeight/2})`);
            var transform = zoomTransform(container.node());
            console.log(transform);
            transform.x = offsetLeft+offsetWidth/2-0.3*(offsetLeft+offsetWidth/2);
            transform.y = offsetTop+offsetHeight/2-0.2*(offsetTop+offsetHeight/2);
        }
        else
        {
            container = svg.append("g");
        }


        //console.dir(container);

        svg.call(zoom().on("zoom", function (event) {
            // console.log("entered");
            // console.dir(event);
            // console.log(event.transform.x);
            // let transform_event = d3.zoomIdentity.translate((event.transform.x+offsetLeft+offsetWidth/2), (event.transform.y+offsetTop+offsetHeight/2)).scale(event.transform.k);

            // container.attr("transform", transform_event);
             container.attr("transform", event.transform);
        }).on("end",function () {
            svg.style("cursor","default");
        }));

        // Clean current svg from nodes and links
        // container.selectAll("g.nodes").remove();
        // container.selectAll("g.links").remove();
        // container.selectAll("text.edgelabel").remove();
        // container.selectAll(".edgepath").remove();
        selectAll("g.nodes").remove();
        selectAll("g.links").remove();
        selectAll("text.edgelabel").remove();
        selectAll(".edgepath").remove();

        var color = scaleOrdinal(schemeCategory10);

        container.append('defs').append('marker')
            // .attrs({'id':'arrowhead',
            //     'viewBox':'-0 -5 10 10',
            //     'refX':26,
            //     'refY':0,
            //     'orient':'auto',
            //     'markerWidth':13,
            //     'markerHeight':13,
            //     'xoverflow':'visible'})
            .attr('id','arrowhead')
            .attr('viewBox','-0 -5 10 10')
            .attr('refX',26)
            .attr('refY',0)
            .attr('orient','auto')
            .attr('markerWidth',13)
            .attr('markerHeight',13)
            .attr('xoverflow','visible')
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', '#999')
            .style('stroke','none');

        container.append('defs').append('marker')
            // .attrs({'id':'arrowheadNOCIRCLE',
            //     'viewBox':'-0 -5 10 10',
            //     'refX':10,
            //     'refY':0,
            //     'orient':'auto',
            //     'markerWidth':13,
            //     'markerHeight':13,
            //     'xoverflow':'visible'})
            .attr('id','arrowheadNOCIRCLE')
            .attr('viewBox','-0 -5 10 10')
            .attr('refX',10)
            .attr('refY',0)
            .attr('orient','auto')
            .attr('markerWidth',13)
            .attr('markerHeight',13)
            .attr('xoverflow','visible')
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', '#999')
            .style('stroke','none');

        var simulation = forceSimulation()
            .force("link", forceLink().id(function (d) {
                return d.id;
            }).distance(200).strength(1))
            .force("charge", forceManyBody().strength(-1000))
            .force("center", forceCenter(width / 2, height / 2));


        var link = container.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("class", "link")
            .attr('marker-end', function(d) {
                if (d["target-size"] == 0) {
                    return 'url(#arrowheadNOCIRCLE)'
                }
                return 'url(#arrowhead)';
            })
            .attr("stroke-width", function (d) {
                return Math.sqrt(d.value);
            });

        link.append("title")
            .text(function (d) {return d.label;});

        let edgepaths = container.selectAll(".edgepath")
            .data(graph.links)
            .enter()
            .append('path')
            .attr('class','edgepath')
            .attr('fill-opacity',0)
            .attr('stroke-opacity',0)
            .attr('id',function (d, i) {return 'edgepath' + i})
            .style("pointer-events", "none");

        let edgelabels = container.selectAll(".edgelabel")
            .data(graph.links)
            .enter()
            .append('text')
            .style("pointer-events", "none")
            .attr('class','edgelabel')
            .attr('font-size',10)
            .attr('fill','#aaa')
            .attr('id',function (d, i) {return 'edgelabel' + i});
            // .attrs({
            //     'class': 'edgelabel',
            //     'id': function (d, i) {return 'edgelabel' + i},
            //     'font-size': 10,
            //     'fill': '#aaa'
            // });

        edgelabels.append('textPath')
            .attr('xlink:href', function (d, i) {return '#edgepath' + i})
            .style("text-anchor", "middle")
            .style("pointer-events", "none")
            .attr("startOffset", "50%")
            .text(function (d) {return d.label});

        var node = container.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(graph.nodes)
            .enter().append("g")

        var circles = node.append("circle")
            .attr("r", function (d) {
                if(d.size != undefined && d.size >= 0)
                    return d.size;
                return 0;
            })
            //.attr("cx", function(d, i) { return d.x+10; })
            //  .attr("cy", function(d, i) { return d.y + 10; })
            .attr("fill", function (d) {
                if(d.color != undefined && d.color != "")
                    return d.color;
                return color("steelblue");
            })
            .call(drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        var lables = node.append("text")
            .text(function (d) {
                return d.label_node;
            })
            .attr('ontology-link', function(d){ if(d["ontology-link"] != undefined){return d["ontology-link"]} return ""; })
            .attr('x', function(d){
                if(d.size > 0)
                {
                    return 8;
                }

                return 6;
            })
            .attr('y', 3)
            .call(drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("title")
            .text(function (d) {
                return d.id;
            });

        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(graph.links);

        function ticked() {
            link
                .attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

            node
                .attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                })

            edgepaths.attr('d', function (d) {
                return 'M ' + d.source.x + ' ' + d.source.y + ' L ' + d.target.x + ' ' + d.target.y;
            });

            edgelabels.attr('transform', function (d) {
                if (d.target.x < d.source.x) {
                    var bbox = this.getBBox();

                    let rx = bbox.x + bbox.width / 2;
                    let ry = bbox.y + bbox.height / 2;
                    return 'rotate(180 ' + rx + ' ' + ry + ')';
                }
                else {
                    return 'rotate(0)';
                }
            });
        }

        function dragstarted(event, d) {
            select(this).style("cursor", "move");
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            select(this).style("cursor", "move");
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            select(this).style("cursor", "default");
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

    }

    useEffect(async () => {

        let URL_report = url_report_JSON;

        if (mode == "development")
        {
            URL_report = url_report_JSON_development;
        }
        let report_json = await fetch(URL_report).then(response => response.json()).then(json => json);

        // console.log(report_json);
        let graph = D3createGraph(report_json);

        console.dir(graph);

        D3_draw_chart(graph);

        SetLoadingFullScreen(false);

        // drawChart()
    // },[svgRef.current])
    },[report_id])

    return(
        <>
        <svg ref={svgRef} id={d3svgchartID} className={"d3-svg"}>
            {/*<g ref={svgGRef} id={d3svgchartgID}></g>*/}
        </svg>
        </>
    )
}

export default D3Graph;