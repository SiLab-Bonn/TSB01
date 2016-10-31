/**
 * ------------------------------------------------------------
 * Copyright (c) SILAB , Physics Institute of Bonn University 
 * ------------------------------------------------------------
 */

`timescale 1ps / 1ps


`include "firmware/src/tsb01.v"
`include "firmware/src/clk_gen.v"

`include "utils/clock_multiplier.v"
`include "utils/clock_divider.v"

`include "utils/bus_to_ip.v"
 
`include "sram_fifo/sram_fifo_core.v"
`include "sram_fifo/sram_fifo.v"

`include "rrp_arbiter/rrp_arbiter.v"

`include "utils/cdc_syncfifo.v"
`include "utils/generic_fifo.v"
`include "utils/cdc_pulse_sync.v"

`include "utils/reset_gen.v"
`include "utils/pulse_gen_rising.v"
`include "utils/CG_MOD_pos.v"
 
`include "spi/spi_core.v"
`include "spi/spi.v"
`include "spi/blk_mem_gen_8_to_1_2k.v"

`include "gpio/gpio.v"

`include "gpac_adc_rx/gpac_adc_iobuf.v"
`include "gpac_adc_rx/gpac_adc_rx.v"
`include "gpac_adc_rx/gpac_adc_rx_core.v"

`include "utils/cdc_reset_sync.v"

`include "utils/ODDR_sim.v"
`include "utils/DCM_sim.v"
`include "utils/BUFG_sim.v"

`include "utils/RAMB16_S1_S9_sim.v"
`include "utils/IBUFDS_sim.v"
`include "utils/IBUFGDS_sim.v"
`include "utils/OBUFDS_sim.v"

`include "utils/fx2_to_bus.v"

`include "pulse_gen/pulse_gen.v"
`include "pulse_gen/pulse_gen_core.v"

`include "seq_gen/seq_gen.v"
`include "seq_gen/seq_gen_core.v"
`include "seq_gen/seq_gen_blk_mem_16x8196.v"
`include "utils/RAMB16_S1_S2_sim.v"

/*
module adc_ser_model ( 
    input wire CLK, LOAD,
    input wire [13:0] DATA_IN,
    output wire DATA_OUT
);

reg [13:0] ser_reg;

always@(posedge CLK)
    if(LOAD)
        ser_reg <= DATA_IN;
    else
        ser_reg <= {ser_reg[12:0], 1'b0};
        
assign DATA_OUT = ser_reg[13];

endmodule
*/

module tb (
    input wire FCLK_IN, 

    //full speed 
    inout wire [7:0] BUS_DATA,
    input wire [15:0] ADD,
    input wire RD_B,
    input wire WR_B,
    
    //high speed
    inout wire [7:0] FD,
    input wire FREAD,
    input wire FSTROBE,
    input wire FMODE,
    
    output ADC_CLK,
    input wire [13:0] ADC_CH0, ADC_CH1, ADC_CH2, ADC_CH3
);   

wire [19:0] SRAM_A;
wire [15:0] SRAM_IO;
wire SRAM_BHE_B;
wire SRAM_BLE_B;
wire SRAM_CE1_B;
wire SRAM_OE_B;
wire SRAM_WE_B;

wire [3:0] ADC_DATA;
wire ADC_ENC, ADC_DCO, ADC_FCO;
wire ADC_SDI;

tsb01 dut(
   
    .FCLK_IN(FCLK_IN), 

    .BUS_DATA(BUS_DATA),
    .ADD(ADD),
    .RD_B(RD_B),
    .WR_B(WR_B),

    .FD(FD), 
    .FREAD(FREAD), 
    .FSTROBE(FSTROBE), 
    .FMODE(FMODE),

    .SRAM_A(SRAM_A), 
    .SRAM_IO(SRAM_IO), 
    .SRAM_BHE_B(SRAM_BHE_B), 
    .SRAM_BLE_B(SRAM_BLE_B), 
    .SRAM_CE1_B(SRAM_CE1_B), 
    .SRAM_OE_B(SRAM_OE_B), 
    .SRAM_WE_B(SRAM_WE_B), 
    
    .ADC_ENC_P(ADC_ENC), 
    .ADC_ENC_N(),
    .ADC_DCO_P(ADC_DCO), 
    .ADC_DCO_N(~ADC_DCO),
    .ADC_FCO_P(ADC_FCO),
    .ADC_FCO_N(~ADC_FCO),
    .ADC_OUT_P(ADC_DATA),
    .ADC_OUT_N(~ADC_DATA),
    
    .ADC_CSN(),
    .ADC_SCLK(),
    .ADC_SDI(ADC_SDI),
    .ADC_SDO(ADC_SDI)
    
);

//SRAM Model
reg [15:0] sram [1048576-1:0];
assign SRAM_IO = !SRAM_OE_B ? sram[SRAM_A] : 16'hzzzz;
always@(negedge SRAM_WE_B)
    sram[SRAM_A] <= SRAM_IO;

clock_multiplier #( .MULTIPLIER(16) ) i_adc_clock_multiplier(.CLK(ADC_ENC),.CLOCK(ADC_DCO));

reg [3:0] adc_cnt;

reg [1:0] adc_rst_syn;
always@(posedge ADC_DCO) begin
    adc_rst_syn <= {adc_rst_syn[0],ADC_ENC};
end

wire adc_rst;
assign adc_rst = adc_rst_syn[0] & !adc_rst_syn[1] ;

localparam [3:0] ADC_SYNC_DLY = 0;
always@(posedge ADC_DCO) begin
    if(adc_rst)
        adc_cnt <= ADC_SYNC_DLY;
    else
        adc_cnt <= adc_cnt + 1;
end

assign ADC_FCO = adc_cnt[3];
assign ADC_CLK = ADC_ENC;

wire adc_load;
assign adc_load = (adc_cnt == 7);
/*
adc_ser_model i_adc_ser0(.CLK(ADC_DCO), .LOAD(adc_load), .DATA_IN(ADC_CH0), .DATA_OUT(ADC_DATA[0]));
adc_ser_model i_adc_ser1(.CLK(ADC_DCO), .LOAD(adc_load), .DATA_IN(ADC_CH1), .DATA_OUT(ADC_DATA[1]));
adc_ser_model i_adc_ser2(.CLK(ADC_DCO), .LOAD(adc_load), .DATA_IN(ADC_CH2), .DATA_OUT(ADC_DATA[2]));
adc_ser_model i_adc_ser3(.CLK(ADC_DCO), .LOAD(adc_load), .DATA_IN(ADC_CH3), .DATA_OUT(ADC_DATA[3]));
*/
assign ADC_DATA = 4'b0110;

initial begin
    $dumpfile("tsb01.vcd");
    $dumpvars(0);
end

endmodule
