#ifndef PUMPCMDPROCESSOR_H
#define PUMPCMDPROCESSOR_H

#include "CmdProcessor.h"
#include "PumpControl.h"

class PumpCmdProcessor : public CmdProcessor
{

    PumpControl* _pPC;

public:
    PumpCmdProcessor(PumpControl* pumpCtrl);
    ~PumpCmdProcessor();
    
    
    void Loop();
    
};

#endif
