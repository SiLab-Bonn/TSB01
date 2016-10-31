/**
 * ------------------------------------------------------------
 * Copyright (c) SILAB , Physics Institute of Bonn University 
 * ------------------------------------------------------------
 *
 */
 
`timescale 1ps / 1ps
 
//`default_nettype none

module tsb01 (

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

    //debug
    output wire [15:0] DEBUG_D,
    output wire LED1,
    output wire LED2,
    output wire LED3,
    output wire LED4,
    output wire LED5,

    inout SDA,
    inout SCL,

    input wire LEMO_TRIGGER,
	 input wire LEMO_RESET,
    input wire LEMO_EX_TRIGGER, // LEMO_RX<2>
    output [2:0] TX,
    input wire RJ45_RESET,
    input wire RJ45_TRIGGER,

    
    //SRAM
    output wire [19:0] SRAM_A,
    inout wire [15:0] SRAM_IO,
    output wire SRAM_BHE_B,
    output wire SRAM_BLE_B,
    output wire SRAM_CE1_B,
    output wire SRAM_OE_B,
    output wire SRAM_WE_B,

    //FADC CONFIG
    output ADC_CSN,
    output ADC_SCLK,
    output ADC_SDI,
    input ADC_SDO,

    //FADC
    output ADC_ENC_P,
    output ADC_ENC_N,
    input ADC_DCO_P,
    input ADC_DCO_N,
    input ADC_FCO_P,
    input ADC_FCO_N,

    input [3:0] ADC_OUT_P,
    input [3:0] ADC_OUT_N,
    
    output RST1_20, //DOUT15
    output RST1_40, //DOUT4
    output RST2_20, //DOUT14
    output RST2_40, //DOUT2
    output RST_ROW_20, //DOUT12
    output RST_ROW_40, //DOUT3
    output CLK_ROW_40, //DOUT6
    output CLK_ROW_20, //DOUT11
    output RST_EN_20, //DOUT10
    output RST_EN_40, //DOUT8
    output CLK_COL, //DOUT1
    output RST_EN_COL, //DOUT0
	
    output DEBUG_ADCSTART,  // debug port DOUT9
    output DEBUG_ADCSYNC  // debug prot DOUT13
);   

    assign SDA = 1'bz;
    assign SCL = 1'bz;

    assign DEBUG_D = 16'ha5a5;

    (* KEEP = "{TRUE}" *)
    wire BUS_CLK; 
    (* KEEP = "{TRUE}" *)
    wire SPI_CLK; 
    (* KEEP = "{TRUE}" *)
    wire ADC_ENC; 
    (* KEEP = "{TRUE}" *)
    wire ADC_CLK;

    wire            RJ45_ENABLED;
    wire            TLU_BUSY;               // busy signal to TLU to deassert trigger
    wire            TLU_CLOCK;
	 
    assign TX[1] = TLU_CLOCK; // trigger clock; also connected to RJ45 output
    //assign TX[2] = TLU_BUSY;
	 
	 //assign RX_LEMO[0]=LEMO_TRIGGER;
	 //assign RX_LEMO[1]=LEMO_RESET;
	 
    ODDR OFDDRRSE_ADC_ENC_BUF(
        .D1(1'b1), 
        .D2(1'b0), 
        .C(ADC_ENC), 
        .CE(1'b1), 
        .R(1'b0), .S(1'b0),
        .Q(TX[0])
    );

    clk_gen_tsb01 i_clkgen(
         .CLKIN(FCLK_IN),
         .BUS_CLK(BUS_CLK),
         .ADC_ENC(ADC_ENC),
         .ADC_CLK(ADC_CLK),
         .SPI_CLK(SPI_CLK),
         .LOCKED()
    );

    // -------  MODULE ADREESSES  ------- //

    
    localparam FIFO_BASEADDR = 16'h0020;                    // 0x0020
    localparam FIFO_HIGHADDR = FIFO_BASEADDR + 15;          // 0x002f

    localparam ADC_RX_CH0_BASEADDR = 16'h0030;                 // 0x0030
    localparam ADC_RX_CH0_HIGHADDR = ADC_RX_CH0_BASEADDR + 15; // 0x003f
    
    localparam ADC_RX_CH1_BASEADDR = ADC_RX_CH0_HIGHADDR + 1;  // 0x0040
    localparam ADC_RX_CH1_HIGHADDR = ADC_RX_CH1_BASEADDR + 15; // 0x004f
    
    localparam ADC_RX_CH2_BASEADDR = ADC_RX_CH1_HIGHADDR + 1;  // 0x0050
    localparam ADC_RX_CH2_HIGHADDR = ADC_RX_CH2_BASEADDR + 15; // 0x005f
    
    localparam ADC_RX_CH3_BASEADDR = ADC_RX_CH2_HIGHADDR + 1;  // 0x0060
    localparam ADC_RX_CH3_HIGHADDR = ADC_RX_CH3_BASEADDR + 15; // 0x006f

    //localparam GPIO_BASEADDR = 16'h0070;
    //localparam GPIO_HIGHADDR = 16'h007f;
    localparam TLU_BASEADDR = ADC_RX_CH3_HIGHADDR+1; //0x0070
    localparam TLU_HIGHADDR = TLU_BASEADDR+16'hFF;   //0x016f
    
    // external trigger
    localparam GPIO_SW_BASEADDR = 16'h0200;  // 0x0200
    localparam GPIO_SW_HIGHADDR = GPIO_SW_BASEADDR + 31; // 0x021f
	 
    localparam PULSE_DELAY_BASEADDR = GPIO_SW_HIGHADDR+1;  // 0x0220
    localparam PULSE_DELAY_HIGHADDR = PULSE_DELAY_BASEADDR + 31; // 0x023f
    
    localparam SPI_ADC_BASEADDR = 16'h0300;                 // 0x0300
    localparam SPI_ADC_HIGHADDR = SPI_ADC_BASEADDR + 16'h8f;    // 0x038f
    
    localparam SEQ_GEN_BASEADDR = 16'h1000;                     // 0x1000
    localparam SEQ_GEN_HIGHADDR = SEQ_GEN_BASEADDR + 15 + 16384;// 0x500f
	 
    wire [15:0] BUS_ADD;
    wire BUS_RD, BUS_WR, BUS_RST;
    
    // -------  BUS SYGNALING  ------- //
    fx2_to_bus i_fx2_to_bus (
        .ADD(ADD),
        .RD_B(RD_B),
        .WR_B(WR_B),

        .BUS_CLK(BUS_CLK),
        .BUS_ADD(BUS_ADD),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR),
        .CS_FPGA()
    );
    
    reset_gen i_reset_gen(.CLK(BUS_CLK), .RST(BUS_RST));

    // -------  USER MODULES  ------- //
    // external trigger
    // switch
    wire [6:0] NOT_CONNECTED;
    wire NEG_EDGE;
	 wire PULSE_EX_TRIGGER;
	 assign PULSE_EX_TRIGGER = NEG_EDGE ? ~LEMO_EX_TRIGGER : LEMO_EX_TRIGGER;
    gpio 
    #( 
        .BASEADDR(GPIO_SW_BASEADDR),
        .HIGHADDR(GPIO_SW_HIGHADDR),
        .IO_WIDTH(8),
        .IO_DIRECTION(8'hff)
    ) i_gpio_sw (
        .BUS_CLK(BUS_CLK),
        .BUS_RST(BUS_RST),
        .BUS_ADD(BUS_ADD),
        .BUS_DATA(BUS_DATA),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR),
        .IO({NOT_CONNECTED,NEG_EDGE})
    );

       // trigger delay
    wire SEQ_EXT_START;
    pulse_gen
    #( 
        .BASEADDR(PULSE_DELAY_BASEADDR), 
        .HIGHADDR(PULSE_DELAY_HIGHADDR)
    ) i_pulse_gen_tdcgate (
        .BUS_CLK(BUS_CLK),
        .BUS_RST(BUS_RST),
        .BUS_ADD(BUS_ADD),
        .BUS_DATA(BUS_DATA),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR),

        .PULSE_CLK(SPI_CLK),
        .EXT_START(PULSE_EX_TRIGGER),
        .PULSE(SEQ_EXT_START)

    );
    assign TX[2]=SEQ_EXT_START;

    wire ADC_EN;
    spi 
    #( 
        .BASEADDR(SPI_ADC_BASEADDR), 
        .HIGHADDR(SPI_ADC_HIGHADDR), 
        .MEM_BYTES(2) 
    )  i_spi_adc
    (
        .BUS_CLK(BUS_CLK),
        .BUS_RST(BUS_RST),
        .BUS_ADD(BUS_ADD),
        .BUS_DATA(BUS_DATA),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR),
		  
		.EXT_START(1'b0),
        .SPI_CLK(SPI_CLK),

        .SCLK(ADC_SCLK),
        .SDI(ADC_SDI),
        .SDO(ADC_SDO),
        .SEN(ADC_EN),
        .SLD()
    );
    assign ADC_CSN = !ADC_EN;

    wire [15:0] SEQ_OUT;
    seq_gen 
    #( 
        .BASEADDR(SEQ_GEN_BASEADDR), 
        .HIGHADDR(SEQ_GEN_HIGHADDR), 
        .MEM_BYTES(8196*2), 
        .OUT_BITS(16) 
    ) i_seq_gen
    (
        .BUS_CLK(BUS_CLK),
        .BUS_RST(BUS_RST),
        .BUS_ADD(BUS_ADD),
        .BUS_DATA(BUS_DATA),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR), 
        
        .SEQ_EXT_START(SEQ_EXT_START),
        .SEQ_CLK(ADC_ENC),
        .SEQ_OUT(SEQ_OUT)
    );

    wire [3:0] ADC_SYNC;
    
    assign RST1_20 = SEQ_OUT[15];
    assign RST1_40 = SEQ_OUT[4];
    assign RST2_40 = SEQ_OUT[2];
    assign RST2_20 = SEQ_OUT[14];
    assign RST_ROW_20 = SEQ_OUT[12];
    assign RST_ROW_40 = SEQ_OUT[3];
    assign CLK_ROW_40 = SEQ_OUT[6];
    assign CLK_ROW_20 = SEQ_OUT[11];
    assign RST_EN_20 = SEQ_OUT[10];
    assign RST_EN_40 = SEQ_OUT[8];
    assign CLK_COL = SEQ_OUT[1];
    assign RST_EN_COL = SEQ_OUT[0];

    assign ADC_SYNC[0] = SEQ_OUT[13];
    assign ADC_SYNC[1] = SEQ_OUT[13];
    assign ADC_SYNC[2] = SEQ_OUT[13];
    assign ADC_SYNC[3] = SEQ_OUT[13];
    assign DEBUG_ADCSYNC = SEQ_OUT[13];
     
    wire [13:0] ADC_IN [3:0];
    wire ADC_DCO, ADC_FCO;
    gpac_adc_iobuf i_gpac_adc_iobuf
    (
        .ADC_CLK(ADC_CLK),
		  
        .ADC_DCO_P(ADC_DCO_P), .ADC_DCO_N(ADC_DCO_N),
        .ADC_DCO(ADC_DCO),
    
        .ADC_FCO_P(ADC_FCO_P), .ADC_FCO_N(ADC_FCO_N),
        .ADC_FCO(ADC_FCO),
    
        .ADC_ENC(ADC_ENC), 
        .ADC_ENC_P(ADC_ENC_P), .ADC_ENC_N(ADC_ENC_N),
    
        .ADC_IN_P(ADC_OUT_P), .ADC_IN_N(ADC_OUT_N),
        
        .ADC_IN0(ADC_IN[0]), 
        .ADC_IN1(ADC_IN[1]), 
        .ADC_IN2(ADC_IN[2]), 
        .ADC_IN3(ADC_IN[3])
    );

    wire [3:0] FIFO_EMPTY_ADC, FIFO_READ;
    wire [31:0] FIFO_DATA_ADC [3:0];
   
    wire [3:0] ADC_ERROR;
    assign {LED2, LED3, LED4, LED5} = ADC_ERROR;
    assign DEBUG_ADCSTART = ADC_ERROR[0];

    genvar i;
    generate
      for (i = 0; i < 4; i = i + 1) begin: adc_gen
        gpac_adc_rx 
        #(
            .BASEADDR(ADC_RX_CH0_BASEADDR+16*i), 
            .HIGHADDR(ADC_RX_CH0_HIGHADDR+16*i),
            .ADC_ID(i), 
            .HEADER_ID(0) 
        ) i_gpac_adc_rx
        (
            .ADC_ENC(ADC_ENC),
            .ADC_IN(ADC_IN[i]),

            .ADC_SYNC(ADC_SYNC[i]),
            .ADC_TRIGGER(1'b0),

            .BUS_CLK(BUS_CLK),
            .BUS_RST(BUS_RST),
            .BUS_ADD(BUS_ADD),
            .BUS_DATA(BUS_DATA),
            .BUS_RD(BUS_RD),
            .BUS_WR(BUS_WR), 

            .FIFO_READ(FIFO_READ[i]),
            .FIFO_EMPTY(FIFO_EMPTY_ADC[i]),
            .FIFO_DATA(FIFO_DATA_ADC[i]),

            .LOST_ERROR(ADC_ERROR[i])
        );
      end
    endgenerate
///////// TLU
    wire TLU_FIFO_READ;
    wire TLU_FIFO_EMPTY;
    wire [31:0] TLU_FIFO_DATA;
    wire TLU_FIFO_PEEMPT_REQ;
	 wire FIFO_FULL;
/*
    tlu_controller #(
        .BASEADDR(TLU_BASEADDR),
        .HIGHADDR(TLU_HIGHADDR),
        .DIVISOR(12)
    ) tlu_controller_module (
        .BUS_CLK(BUS_CLK),
        .BUS_RST(BUS_RST),
        .BUS_ADD(BUS_ADD),
        .BUS_DATA(BUS_DATA),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR),
        
        .FIFO_READ(TLU_FIFO_READ),
        .FIFO_EMPTY(TLU_FIFO_EMPTY),
        .FIFO_DATA(TLU_FIFO_DATA),
		  
        .FIFO_PREEMPT_REQ(TLU_FIFO_PEEMPT_REQ),
        
        .RJ45_TRIGGER(RJ45_TRIGGER),
        .LEMO_TRIGGER(LEMO_TRIGGER),
        .RJ45_RESET(RJ45_RESET),
        .LEMO_RESET(LEMO_RESET),
        
        .RJ45_ENABLED(RJ45_ENABLED),
        .TLU_BUSY(TLU_BUSY),
        .TLU_CLOCK(TLU_CLOCK),
        
        .EXT_VETO(FIFO_FULL),
    
        .CMD_CLK(BUS_CLK), // signals used for FEI4
        .CMD_READY(1'b0), // signals used for FEI4
        .CMD_EXT_START_FLAG(), // to trigger command sequencer signals used for FEI4
        .CMD_EXT_START_ENABLE(1'b1), // signals used for FEI4, if 0: busy is high after config, if 1: busy is low after config
        
        .TIMESTAMP()
    );*/
///// FIFO and arbiter
    wire ARB_READY_OUT, ARB_WRITE_OUT;
    wire [31:0] ARB_DATA_OUT;
    rrp_arbiter 
    #( 
//        .WIDTH(5)
			.WIDTH(4)
    ) i_rrp_arbiter
    (
        .RST(BUS_RST),
        .CLK(BUS_CLK),
    
/*        .WRITE_REQ({~FIFO_EMPTY_ADC,~TLU_FIFO_EMPTY}),
        .HOLD_REQ({4'b0, TLU_FIFO_PEEMPT_REQ}),
        .DATA_IN({FIFO_DATA_ADC[3],FIFO_DATA_ADC[2],FIFO_DATA_ADC[1],FIFO_DATA_ADC[0],TLU_FIFO_DATA}),
        .READ_GRANT({FIFO_READ,TLU_FIFO_READ}),*/
		  
		  .WRITE_REQ({~FIFO_EMPTY_ADC}),
        .HOLD_REQ({4'b0}),
        .DATA_IN({FIFO_DATA_ADC[3],FIFO_DATA_ADC[2],FIFO_DATA_ADC[1],FIFO_DATA_ADC[0]}),
        .READ_GRANT({FIFO_READ}),

        .READY_OUT(ARB_READY_OUT),
        .WRITE_OUT(ARB_WRITE_OUT),
        .DATA_OUT(ARB_DATA_OUT)
    );
    
    wire USB_READ;
    assign USB_READ = FREAD && FSTROBE;
    sram_fifo 
    #(
        .BASEADDR(FIFO_BASEADDR), 
        .HIGHADDR(FIFO_HIGHADDR)
    ) i_out_fifo (
        .BUS_CLK(BUS_CLK),
        .BUS_RST(BUS_RST),
        .BUS_ADD(BUS_ADD),
        .BUS_DATA(BUS_DATA),
        .BUS_RD(BUS_RD),
        .BUS_WR(BUS_WR), 
        
        .SRAM_A(SRAM_A),
        .SRAM_IO(SRAM_IO),
        .SRAM_BHE_B(SRAM_BHE_B),
        .SRAM_BLE_B(SRAM_BLE_B),
        .SRAM_CE1_B(SRAM_CE1_B),
        .SRAM_OE_B(SRAM_OE_B),
        .SRAM_WE_B(SRAM_WE_B),

        .USB_READ(USB_READ),
        .USB_DATA(FD),

        .FIFO_READ_NEXT_OUT(ARB_READY_OUT),
        .FIFO_EMPTY_IN(!ARB_WRITE_OUT),
        .FIFO_DATA(ARB_DATA_OUT),

        .FIFO_NOT_EMPTY(),
        .FIFO_READ_ERROR(),
        .FIFO_FULL(FIFO_FULL),
        .FIFO_NEAR_FULL(LED1)    
    );

endmodule
