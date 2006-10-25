// -*- mode:C++; tab-width:8; c-basic-offset:2; indent-tabs-mode:t -*- 
/*
 * Ceph - scalable distributed file system
 *
 * Copyright (C) 2004-2006 Sage Weil <sage@newdream.net>
 *
 * This is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License version 2.1, as published by the Free Software 
 * Foundation.  See file COPYING.
 * 
 */

#ifndef __LOGEVENT_H
#define __LOGEVENT_H

#define EVENT_STRING       1
#define EVENT_INODEUPDATE  2
#define EVENT_DIRUPDATE    3
#define EVENT_UNLINK       4
#define EVENT_ALLOC        5


#include <string>
using namespace std;

#include "include/buffer.h"
#include "include/Context.h"

class MDS;

// generic log event
class LogEvent {
 private:
  int _type;
  off_t _end_off;
  friend class MDLog;

 public:
  LogEvent(int t) : _type(t), _end_off(0) { }
  virtual ~LogEvent() { }

  // encoding
  virtual void encode_payload(bufferlist& bl) = 0;
  virtual void decode_payload(bufferlist& bl, int& off) = 0;
  static LogEvent *decode(bufferlist &bl);


  virtual void print(ostream& out) { 
    out << "event(" << _type << ")";
  }


  /*** live journal ***/

  /* obsolete() - is this entry committed to primary store, such that
   *   we can expire it from the journal?
   */
  virtual bool can_expire(MDS *m) {
    return true;
  }
  
  /* retire() - prod MDS into committing hte relevant state so that this
   *   entry can be expired from the jorunal.
   */
  virtual void retire(MDS *m, Context *c) {
    c->finish(0);
    delete c;
  }

  
  /*** recovery ***/

  /* has_happened() - true if this event has already been applied.
   */
  virtual bool has_happened(MDS *m) { return true; }

  /* replay() - replay given event
   */
  virtual void replay(MDS *m) { assert(0); }

};

inline ostream& operator<<(ostream& out, LogEvent& le) {
  le.print(out);
  return out;
}

#endif
