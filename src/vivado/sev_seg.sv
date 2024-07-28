`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/21/2024 10:58:45 AM
// Design Name: 
// Module Name: sev_seg
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module sev_seg(

	input [7:0] in,
    input clk,
    output reg [6:0] a_to_g,
    output reg [3:0] an,
    output wire dp 
	 );
	 
	 

    assign dp = 1;
    assign an = 4'b0111; // only need one digit display
	
	//decoder or truth-table for 7a_to_g display values
	always_comb begin 

        case(in)
            //////////<---MSB-LSB<---
            //////////////gfedcba////////////////////////////////////////////              a
            0:a_to_g = 7'b1000000;////0000												   __					
            1:a_to_g = 7'b1111001;////0001												f/	  /b
            2:a_to_g = 7'b0100100;////0010												  g
            //                                                                           __	
            3:a_to_g = 7'b0110000;////0011										 	 e /   /c
            4:a_to_g = 7'b0011001;////0100												 __
            5:a_to_g = 7'b0010010;////0101                                               d  
            6:a_to_g = 7'b0000010;////0110
            7:a_to_g = 7'b1111000;////0111
            8:a_to_g = 7'b0000000;////1000
            9:a_to_g = 7'b0010000;////1001
            'hA:a_to_g = 7'b0111111; // dash-(g)
            'hB:a_to_g = 7'b1111111; // all turned off
            'hC:a_to_g = 7'b1110111;
            
            default: a_to_g = 7'b1111111; // U       
        endcase
        
    end 


endmodule